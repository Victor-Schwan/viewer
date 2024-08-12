#ifndef MyViewerProc_h
#define MyViewerProc_h 1

#include "marlin/Processor.h"
#include "EventDisplayer.h"

class MyViewerProc : public marlin::Processor, EventDisplayer {
    friend class EventDisplayer;
    public:
        MyViewerProc(const MyViewerProc&) = delete;
        MyViewerProc& operator=(const MyViewerProc&) = delete;

        marlin::Processor* newProcessor() { return new MyViewerProc; }

        MyViewerProc();
        ~MyViewerProc();
        // void init(){};
        void processEvent(EVENT::LCEvent* evt);
        // void end(){};

    private:
        int _nEvent{};
        float _bField{};
};

#endif