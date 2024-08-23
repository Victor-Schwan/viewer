import os

from Configurables import (
    ApplicationMgr,
    EDM4hep2LcioTool,
    GeoSvc,
    Lcio2EDM4hepTool,
    LcioEvent,
    MarlinProcessorWrapper,
    PodioInput,
    PodioOutput,
    k4DataSvc,
)
from Gaudi.Configuration import DEBUG, INFO
from k4FWCore.parseArgs import parser
from k4MarlinWrapper.inputReader import attach_edm4hep2lcio_conversion, create_reader

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
    metavar=("file1", "file2"),
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

if reco_args.inputFiles:
    read = create_reader(reco_args.inputFiles, evtsvc)
    read.OutputLevel = INFO
    algList.append(read)
else:
    read = None


MyStatusmonitor = MarlinProcessorWrapper("MyStatusmonitor")
MyStatusmonitor.OutputLevel = INFO
MyStatusmonitor.ProcessorType = "Statusmonitor"
MyStatusmonitor.Parameters = {"HowOften": ["1"]}
algList.append(MyStatusmonitor)

MyViewer = MarlinProcessorWrapper("MyViewerProc")
MyViewer.OutputLevel = INFO
MyViewer.ProcessorType = "MyViewerProc"
MyViewer.Parameters = {"eventDisplay": ["true"]}

algList.append(MyViewer)

attach_edm4hep2lcio_conversion(algList, read)

ApplicationMgr(
    TopAlg=algList, EvtSel="NONE", EvtMax=3, ExtSvc=svcList, OutputLevel=INFO
)
