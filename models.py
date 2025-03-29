from IClassesModels import IProcess, IProcessManager, IStateProcess

class Process(IProcess):
    def __init__(self, pid, burst_time, arrive_time=0):
        self.pid = pid
        self.burst_time = burst_time
        self.arrive_time = arrive_time  # Agregar arrive_time como atributo
        
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
        
class ProcessManager:
    def __init__(self):
        self.processes = []
        self.states = []

    def execute_processes(self):
        self.states = []
        current_time = 0

        for process in self.processes:
            start_time = max(current_time, process.arrive_time)
            finish_time = start_time + process.burst_time
            turnaround_time = finish_time - process.arrive_time
            waiting_time = start_time - process.arrive_time

            self.states.append({
                "PID": process.pid,
                "Start Time": start_time,
                "Finish Time": finish_time,
                "Turnaround Time": turnaround_time,
                "Waiting Time": waiting_time,
            })

            current_time = finish_time

class Batch:
    def __init__(self, batch_id):
        self.batch_id = batch_id
        self.processes = []

    def add_process(self, process):
        self.processes.append(process)

    def get_processes(self):
        return self.processes