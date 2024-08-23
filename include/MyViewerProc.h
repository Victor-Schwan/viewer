#ifndef MYVIEWERPROC_H
#define MYVIEWERPROC_H

#include "EventDisplayer.h"
#include "marlin/Processor.h"

class MyViewerProc : public marlin::Processor, EventDisplayer
{
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

#endif // MYVIEWERPROC_H