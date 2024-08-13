#include "MyViewerProc.h"

#include "marlin/Global.h"
#include "marlinutil/GeometryUtil.h"
#include "marlinutil/CalorimeterHitType.h"
#include "UTIL/LCRelationNavigator.h"
#include "UTIL/TrackTools.h"
#include "CLHEP/Random/Randomize.h"

#include "EVENT/TrackState.h"
#include "UTIL/Operators.h"
#include "UTIL/TrackTools.h"
#include "marlinutil/DDMarlinCED.h"
#include "marlinutil/CalorimeterHitType.h"

// #include <edm4hep/TrackerHitPlaneCollection.h>
#include <stdexcept> // For std::invalid_argument

MyViewerProc mvp;

MyViewerProc::MyViewerProc() : marlin::Processor("MyViewerProc"), EventDisplayer(this)
{
    _description = "";
}

MyViewerProc::~MyViewerProc()
{
}

void displayTrack(EVENT::Track *track, unsigned long color)
{
    if (track == nullptr)
        return;

    double bField = MarlinUtil::getBzAtOrigin();

    auto ts = track->getTrackState(TrackState::AtIP);
    double xs = ts->getReferencePoint()[0] - ts->getD0() * sin(ts->getPhi());
    double ys = ts->getReferencePoint()[1] + ts->getD0() * cos(ts->getPhi());
    double zs = ts->getReferencePoint()[2] + ts->getZ0();
    double pt = bField * 3e-4 / std::abs(ts->getOmega());
    double charge = (ts->getOmega() > 0. ? 1. : -1.);
    double px = pt * std::cos(ts->getPhi());
    double py = pt * std::sin(ts->getPhi());
    double pz = pt * ts->getTanLambda();

    // void DDMarlinCED::drawHelix(float b, float charge, float x, float y, float z,
    //                       float px, float py, float pz, int marker, int size, unsigned int col,
    //                       float rmin, float rmax, float zmax, unsigned int id)  {
    DDMarlinCED::drawHelix(bField, charge, xs, ys, zs, px, py, pz, 1, 1, color, 0.0, 1804., 2200.);

    // plot settings for tracker hits
    int type = 0; // point
    int size = 4; // larger point
    auto hits = track->getTrackerHits();
    // std::find
    for (auto *hit : hits)
    {
        auto pos = hit->getPosition();
        ced_hit(pos[0], pos[1], pos[2], type, size, color);
    }
}

void displayHitCol(EVENT::LCCollection *hits, unsigned long color = 0xFFFFFF) // Default color: white (0xFFFFFF)
{
    if (hits == nullptr)
    {
        throw std::invalid_argument("Hit collection pointer is null.");
    }

    int type = 0; // point
    int size = 4; // larger point

    for (size_t i = 0; i < hits->getNumberOfElements(); i++)
    {
        auto hit = (TrackerHitPlane *)hits->getElementAt(i);
        auto pos = hit->getPosition();
        ced_hit(pos[0], pos[1], pos[2], type, size, color);
    }
}

// void MyViewerProc::processEvent(EVENT::LCEvent* evt){
//     LCCollection* conformalTracks = evt->getCollection("SiTracksCT");
//     LCCollection* clupatraTracks = evt->getCollection("ClupatraTracks");

//     std::cout<<"NUMBER OF CONFORMAL TRACKS: "<< conformalTracks->getNumberOfElements() <<std::endl;
//     std::cout<<"NUMBER OF TPC TRACKS: "<< clupatraTracks->getNumberOfElements() <<std::endl;

//     for (int i=0; i<conformalTracks->getNumberOfElements(); ++i){

//         auto track = static_cast <Track*> ( conformalTracks->getElementAt(i) );
//         std::cout<<"TRACK: "<< track <<std::endl;

//         drawDisplay(this, evt, displayTrack, track, 0x00ff00);
//     }
// }

void MyViewerProc::processEvent(EVENT::LCEvent *evt)
{
    LCCollection *conformalTracks = evt->getCollection("SiTracksCT");
    LCCollection *clupatraTracks = evt->getCollection("ClupatraTracks");
    LCCollection *vertexBarrelHits = evt->getCollection("VertexBarrelTrackerHits");

    int numConformalTracks = conformalTracks->getNumberOfElements();
    int numClupatraTracks = clupatraTracks->getNumberOfElements();

    std::cout << "NUMBER OF CONFORMAL TRACKS: " << numConformalTracks << std::endl;
    std::cout << "NUMBER OF TPC TRACKS: " << numClupatraTracks << std::endl;

    // Determine the maximum number of elements between the two collections
    int maxTracks = std::max(numConformalTracks, numClupatraTracks);

    for (int i = 0; i < maxTracks; ++i)
    {
        // Process conformal tracks if within bounds
        if (i < numConformalTracks)
        {
            auto track = static_cast<Track *>(conformalTracks->getElementAt(i));
            streamlog_out(DEBUG0) << "CONFORMAL TRACK: " << track << std::endl;
            drawDisplay(this, evt, displayTrack, track, 0x00ff00);
        }

        // Process clupatra tracks if within bounds
        if (i < numClupatraTracks)
        {
            auto track = static_cast<Track *>(clupatraTracks->getElementAt(i));
            std::cout << "CLUPATRA TRACK: " << track << std::endl;
            drawDisplay(this, evt, displayTrack, track, 0xff0000);
        }
    }
    drawDisplay(this, evt, displayHitCol, vertexBarrelHits, 0xFFFFFF);
}
