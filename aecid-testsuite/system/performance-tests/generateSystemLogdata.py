# This file can be used to test the VariableTypeDetector. It provides discrete
# and continuous data measured from the running system.

import psutil
import time
import sys
from datetime import datetime
import multiprocessing

with open('/tmp/results.csv', 'a+', buffering=100) as file:
    string = ''
    string += 'time,aminerCpuUsage,aminerMemUsage,'
    for i in range(multiprocessing.cpu_count()):
        string += "cpu%d,"%(i+1)
    string += 'vmTotal,vmAvailable,vmPercent,vmUsed,vmFree\n'
    startTime = time.time()
    endTime = startTime + int(sys.argv[1])
    p = None
    ppid = None
    firstRead = False
    while time.time() < endTime:
        t = time.time()
        for proc in psutil.process_iter():
            if psutil.pid_exists(proc.pid) and proc.name() == "AMiner":
                pid = proc.pid
                if p is None or pid > ppid:
                    ppid = pid
                    p = psutil.Process(ppid)
                    firstRead = True

        if psutil.pid_exists(ppid):
            aminerCpu = str(p.cpu_percent(interval=0.0))
            mem = "%.2f"%p.memory_percent()
        else:
            aminerCpu = '-'
            mem = '-'
        cpus = psutil.cpu_percent(percpu=True)
        dt = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
        vm = psutil.virtual_memory()
        cpu = ""
        for i in range(multiprocessing.cpu_count()):
            cpu = cpu + str(cpus[i]) + ','
        if firstRead is True:
            firstRead = False
        else:
            string += "%s,%s,%s,%s%s,%s,%s,%s,%s\n"%(dt, aminerCpu, mem, cpu, vm[0], vm[1], vm[2], vm[3], vm[4])
        delta = time.time()-t
        if delta < 1:
            time.sleep(1-delta)

    file.write(string)
    file.close()
