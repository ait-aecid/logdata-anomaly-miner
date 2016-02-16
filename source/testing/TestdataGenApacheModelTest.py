#!/usr/bin/python -BEsSt

import os
import sys

sys.path=sys.path[1:]+['/home/rfiedler/cais-cluster/AECID/ProductionComponent/source/testing', '/home/rfiedler/cais-cluster/AECID/ProductionComponent/source/root/usr/lib/aminer', '/usr/lib/python2.7/dist-packages']

import ByteLineReader
import FirstMatchModelElement
import MatchContext
import SequenceModelElement

debugFlag=False
inputFd=0

argPos=1
while argPos < len(sys.argv):
  argName=sys.argv[argPos]
  argPos+=1
  if argName == '--Debug':
    debugFlag=True
    continue
  if argName == '--File':
    inputFd=os.open(sys.argv[argPos], os.O_RDONLY|os.O_NOCTTY)
    argPos+=1
    continue
  print >>sys.stderr, "Unknown argument %s" % argName
  sys.exit(1)

if debugFlag:
  from InteractiveSysExceptionHook import overrideExceptHook
  overrideExceptHook()

serviceChildren=[]

import ConfigAhitApacheLineModel
serviceChildren+=[ConfigAhitApacheLineModel.getModel()]

import ConfigSyslogPreambleModel
syslogPreambleModel=ConfigSyslogPreambleModel.getModel()
model=SequenceModelElement.SequenceModelElement('model', [syslogPreambleModel, FirstMatchModelElement.FirstMatchModelElement('services', serviceChildren)])

byteLineReader=ByteLineReader.ByteLineReader(inputFd, 1<<16)
while True:
  lineData=byteLineReader.readLine()
  if (lineData==None): break
  if debugFlag:
    print >>sys.stderr, "Got line: %s" % lineData
  matchContext=MatchContext.MatchContext(lineData)
  match=model.getMatchElement('', matchContext)
  if match == None:
    print >>sys.stderr, "Match data: (none)"
  else:
    print >>sys.stderr, "Match data:\n%s\nRemaining: %s" % (match.annotateMatch(''), matchContext.matchData)

# FIXME: MatchPathState
