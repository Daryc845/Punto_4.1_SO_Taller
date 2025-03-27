from IClassesModels import IProcess, IProcessManager, IStateProcess

class Process(IProcess):
    def __init__(self, pid, burstTime):
        self.burstTime = burstTime
        self.pid = pid
        
class StateProcess(IStateProcess):
    def __init__(self, process, arriveTime, completionTime = None, turnaroundTime = None, waitingTime = None):
        self.process = process
        self.arriveTime = arriveTime
        self.completionTime = completionTime
        self.waitingTime = waitingTime
        self.turnaroundTime = turnaroundTime
        
    def finishProcess(self, completionTime):
        self.completionTime = completionTime
        self.turnaroundTime = self.completionTime - self.arriveTime
        self.waitingTime = self.turnaroundTime - self.process.burstTime
        
    def getValues(self):
        return (self.process.pid, self.arriveTime, self.process.burstTime, self.completionTime, self.turnaroundTime, self.waitingTime)
        
class ProcessManager(IProcessManager):
    def __init__(self):
        self.processes = []
        self.processStates = []
        self.currentTime = 0
        
    def addProcess(self, pid, arriveTime,burstTime):
        process = Process(pid, burstTime)
        processState = StateProcess(process, arriveTime)
        self.processStates.append(processState)
        
    def run(self):
        self.currentTime = 0
        self.processStates.sort(key=lambda x: x.arriveTime)
        
        for i in range (len(self.processStates)):
            if i > 0:
                self.currentTime = self.processStates[i-1].completionTime
            else:
                self.currentTime = self.processStates[i].arriveTime
            self.currentTime += self.processStates[i].process.burstTime
            self.processStates[i].finishProcess(self.currentTime)
        return self.processStates
    
    def pidRegistered(self, pid):
        for process in self.processStates:
            if process.process.pid == pid:
                return True
        return False
            
    def getProcessStates(self):
        return self.processStates