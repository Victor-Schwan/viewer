import os
import sys
from pathlib import Path

from Configurables import (
    ApplicationMgr,
    EDM4hep2LcioTool,
    GeoSvc,
    Lcio2EDM4hepTool,
    LcioEvent,
    MarlinProcessorWrapper,
    PodioInput,
    PodioOutput,
    TrackingCellIDEncodingSvc,
    k4DataSvc,
)
from Gaudi.Configuration import DEBUG, INFO

try:
    from k4FWCore.utils import SequenceLoader, import_from
except ImportError:
    from py_utils import import_from, SequenceLoader

from k4FWCore.parseArgs import parser
from k4MarlinWrapper.parseConstants import parseConstants

# only non-FCCMDI models, later FCCMDI models are added to this tuple
DETECTOR_MODELS = (
    "ILD_l2_v02",
    "ILD_l4_o1_v02",
    "ILD_l4_o2_v02",
    "ILD_l5_o1_v02",
    "ILD_l5_o1_v03",
    "ILD_l5_o1_v04",
    "ILD_l5_o1_v05",
    "ILD_l5_o1_v06",
    "ILD_l5_o2_v02",
    "ILD_l5_o3_v02",
    "ILD_l5_o4_v02",
    "ILD_s2_v02",
    "ILD_s4_o1_v02",
    "ILD_s4_o2_v02",
    "ILD_s5_o1_v02",
    "ILD_s5_o1_v03",
    "ILD_s5_o1_v04",
    "ILD_s5_o1_v05",
    "ILD_s5_o1_v06",
    "ILD_s5_o2_v02",
    "ILD_s5_o3_v02",
    "ILD_s5_o4_v02",
)
# only FCCMDI
FCCeeMDI_DETECTOR_MODELS = (
    "ILD_l5_o1_v09",
    "ILD_l5_v11",
)
DETECTOR_MODELS = DETECTOR_MODELS + FCCeeMDI_DETECTOR_MODELS

parser.add_argument(
    "--inputFiles",
    action="extend",
    nargs="+",
    metavar=["file1", "file2"],
    help="One or multiple input files",
)
parser.add_argument(
    "--compactFile", help="Compact detector file to use", type=str, default=""
)
parser.add_argument(
    "--detectorModel",
    help="Which detector model to run reconstruction for",
    choices=DETECTOR_MODELS,
    type=str,
    default="ILD_l5_v11",
)


reco_args = parser.parse_known_args()[0]

algList = []
svcList = []

evtsvc = k4DataSvc("EventDataSvc")
svcList.append(evtsvc)

det_model = reco_args.detectorModel
if reco_args.compactFile:
    compact_file = reco_args.compactFile
else:
    compact_file = f"{os.path.normpath(os.environ['k4geo_DIR'])}/ILD/compact/{det_model}/{det_model}.xml"

geoSvc = GeoSvc("GeoSvc")
geoSvc.detectors = [compact_file]
geoSvc.OutputLevel = INFO
geoSvc.EnableGeant4Geo = False
svcList.append(geoSvc)

cellIDSvc = TrackingCellIDEncodingSvc("CellIDSvc")
cellIDSvc.EncodingStringParameterName = "GlobalTrackerReadoutID"
cellIDSvc.GeoSvcName = geoSvc.name()
cellIDSvc.OutputLevel = INFO
svcList.append(cellIDSvc)


def create_reader(input_files):
    """Create the appropriate reader for the input files"""
    if input_files[0].endswith(".slcio"):
        if any(not f.endswith(".slcio") for f in input_files):
            print("All input files need to have the same format (LCIO)")
            sys.exit(1)

        read = LcioEvent()
        read.Files = input_files
    else:
        if any(not f.endswith(".root") for f in input_files):
            print("All input files need to have the same format (EDM4hep)")
            sys.exit(1)
        read = PodioInput("PodioInput")
        global evtsvc
        evtsvc.inputs = input_files

    return read


if reco_args.inputFiles:
    read = create_reader(reco_args.inputFiles)
    read.OutputLevel = INFO
    algList.append(read)
else:
    read = None


MyAIDAProcessor = MarlinProcessorWrapper("MyAIDAProcessor")
MyAIDAProcessor.OutputLevel = INFO
MyAIDAProcessor.ProcessorType = "AIDAProcessor"
MyAIDAProcessor.Parameters = {
    "Compress": ["1"],
    "FileType": ["root"],
}
algList.append(MyAIDAProcessor)

# We need to convert the inputs in case we have EDM4hep input
if isinstance(read, PodioInput):
    EDM4hep2LcioInput = EDM4hep2LcioTool("InputConversion")
    EDM4hep2LcioInput.convertAll = True
    # Adjust for the different naming conventions
    EDM4hep2LcioInput.collNameMapping = {"MCParticles": "MCParticle"}
    MyAIDAProcessor.EDM4hep2LcioTool = EDM4hep2LcioInput


MyStatusmonitor = MarlinProcessorWrapper("MyStatusmonitor")
MyStatusmonitor.OutputLevel = INFO
MyStatusmonitor.ProcessorType = "Statusmonitor"
MyStatusmonitor.Parameters = {"HowOften": ["1"]}
algList.append(MyStatusmonitor)

MyViewer = MarlinProcessorWrapper("MyViewerProc")
MyViewer.OutputLevel = INFO
MyViewer.ProcessorType = "MyViewerProc"
MyViewer.Parameters = {"eventDisplay":["true"]}

algList.append(MyViewer)

ApplicationMgr(
    TopAlg=algList, EvtSel="NONE", EvtMax=3, ExtSvc=svcList, OutputLevel=INFO
)
