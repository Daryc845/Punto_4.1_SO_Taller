from abc import ABC, abstractmethod

class IProcess(ABC):
    @abstractmethod
    def __init__(self, pid, burstTime):
        pass

class IStateProcess(ABC):
    @abstractmethod
    def __init__(self, process, arriveTime, completionTime=None, turnaroundTime=None, waitingTime=None):
        pass

    @abstractmethod
    def finishProcess(self, completionTime):
        pass

    @abstractmethod
    def getValues(self):
        pass

class IProcessManager(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def addProcess(self, pid, arriveTime, burstTime):
        pass

    @abstractmethod
    def runSerie(self):
        pass

    @abstractmethod
    def pidRegisteredInList(self, pid):
        pass
    
    @abstractmethod
    def pidRegisteredInList(self, processStates, pid, index=None):
        pass

class ISerieProcessingView(ABC):
    @abstractmethod
    def __init__(self, addProcess, runAnimation):
        pass

    @abstractmethod
    def drawAnimation(self, processStates):
        pass

    @abstractmethod
    def showErrorMessage(self, message):
        pass

    @abstractmethod
    def cleanRows(self):
        pass

    @abstractmethod
    def cleanInputs(self):
        pass

    @abstractmethod
    def addTableValues(self, processStates):
        pass
    
class ISerieProcessingController(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def addProcess(self):
        pass
    
    @abstractmethod
    def runAnimation(self):
        pass
    
    @abstractmethod
    def run(self):
        pass