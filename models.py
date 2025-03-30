from IClassesModels import IProcess, IProcessManager, IStateProcess
import copy

class Process(IProcess):
    def __init__(self, pid, burstTime):
        """
        Construye un objeto Process, este objeto representa un proceso en el sistema operativo.
        El PID es el identificador del proceso y el burstTime es el tiempo en la CPU que necesita el proceso
        para su ejecución. Adicionalmente inicializa la variable burstTimeLeft, esta variable lleva el conteo
        de tiempo de rafaga que le falta por ejecutarse al proceso y se inicia igual al tiempo de rafaga.

        Args:
            pid (int): Identificador único del proceso.
            burstTime (int): Tiempo requerido en la CPU para la ejecución completa del proceso.
        """
        self.burstTime = burstTime
        self.burstTimeLeft = burstTime
        self.pid = pid
        
class StateProcess(IStateProcess):
    def __init__(self, process, arrivalTime, completionTime=None, turnaroundTime=None, waitingTime=None):
        """
        Construye un objeto StateProcess, este objeto representa el estado de un proceso en el sistema operativo.
        El objeto process de tipo Process representa el proceso, el arrivalTime es el tiempo de llegada del proceso,
        el completionTime es el tiempo donde finalizó del proceso, el turnaroundTime es la suma de todos los tiempos de ejecución
        con la suma de todos los tiempos de espera y el waitingTime es la suma de los tiempos en el que el proceso ha estado 
        esperando tiempo en la CPU.

        Args:
            process (Process): Objeto Process asociado a este estado.
            arrivalTime (int): Tiempo de llegada del proceso al sistema.
            completionTime (int, optional): Tiempo de finalización del proceso. Defaults to None.
            turnaroundTime (int, optional): Tiempo total desde llegada hasta finalización. Defaults to None.
            waitingTime (int, optional): Tiempo total que el proceso estuvo esperando. Defaults to None.
        """
        self.process = process
        self.arrivalTime = arrivalTime
        self.completionTime = completionTime
        self.waitingTime = waitingTime
        self.turnaroundTime = turnaroundTime
    
    def finishProcess(self, completionTime):
        """
        Finaliza el proceso, por ende se le asigna el tiempo de finalización(completionTime), se calcula el turnaroundTime
        segun la formula(completionTime - arrivalTime) y se calcula el waitingTime segun la formula(turnaroundTime - burstTime), teniendo en cuenta
        que el burstTime es el burstTime correspondiente del objeto process.

        Args:
            completionTime (int): Tiempo en que el proceso finaliza su ejecución.
        """
        self.completionTime = completionTime
        self.turnaroundTime = self.completionTime - self.arrivalTime
        self.waitingTime = self.turnaroundTime - self.process.burstTime
    
    def getValues(self):
        """
        Devuelve una tupla que contiene los valores del objeto StateProcess, en el orden pid, arrivalTime, burstTime, completionTime, turnaroundTime y waitingTime.

        Returns:
            tuple: (pid, arrivalTime, burstTime, completionTime, turnaroundTime, waitingTime)
        """
        return (self.process.pid, self.arrivalTime, self.process.burstTime, 
                self.completionTime, self.turnaroundTime, self.waitingTime)
        
class ProcessManager(IProcessManager):
    def __init__(self):
        """
        Construye un objeto ProcessManager, este objeto permite gestionar varios procesos de un sistema operativo,
        este objeto maneja la logica de procesamiento segun esquemas de procesamiento particulares
        tales como procesamiento en serie, procesamiento en lotes con mono y multiprogramación y procesamiento
        de tiempo compartido(Round Robin). Los procesos son almacenados en la tupla processStates, ademas
        utiliza la variable currentTime para llevar un registro del tiempo actual de ejecución de la CPU.
        """
        self.processStates = []
        self.currentTime = 0
        
    def addProcess(self, pid, arrivalTime, burstTime):
        """
        Añade un proceso en la ultima posición de la cola de procesos del objeto ProcessManager.

        Args:
            pid (int): Identificador único del proceso.
            arrivalTime (int): Tiempo de llegada del proceso a la cola.
            burstTime (int): Tiempo que requiere el proceso en la CPU para su ejecución.

        Returns:
            None
        """
        process = Process(pid, burstTime)
        processState = StateProcess(process, arrivalTime)
        self.processStates.append(processState)
    
    def runSerie(self):
        """
        Simula el procesamiento de todos los procesos registrados en la tupla processStates segun el esquema de procesamiento en serie.
        En este caso se ordenan los procesos de la tupla por el tiempo de llegada y se ejecutan uno a uno, para ello utiliza la variable
        currentTime, con esta calcula el tiempo que demoro un proceso en ejecutarse, una vez es ejecutado el proceso se le asigna tiempo de finalización
        usando el metodo finishProcess del objeto StateProcess(el proceso) correspondiente, este metodo calcula el turnaroundTime y el waitingTime.

        Returns:
            list: La tupla processStates con los procesos ya ejecutados y organizados.
        """
        self.currentTime = 0
        
        self.processStates.sort(key=lambda x: x.arrivalTime)
        for i in range (len(self.processStates)):
            if i > 0:
                self.currentTime = self.processStates[i-1].completionTime
            else:
                self.currentTime = self.processStates[i].arrivalTime
            self.currentTime += self.processStates[i].process.burstTime
            self.processStates[i].finishProcess(self.currentTime)
    
        return self.processStates
    
    def runRoundRobin(self, quantum):
        """
        Simula el procesamiento de todos los procesos registrados en la tupla processStates segun el esquema de procesamiento de tiempo compartido(Round Robin).
        En este caso se ordenan los procesos de la tupla por el tiempo de llegada, luego se inicializa una lista auxiliar, sobre este lista se hara el procesamiento
        dependiendo si el quantum es 1 o mayor mediante el metodo initializeProcessStatesAux.
        Luego de que se inicialize la lista auxiliar se recorre usando el indice i, en la primera iteracion se le asigna al currentTime(tiempo actual) el tiempo de llegada del primer proceso, 
        para no evaluar sin razon alguna los primeros segundos donde no ha llegado ningun proceso, entonces se evalua si el burstTime debe reducirse, esto es porque el metodo genera copias de cada uno de los procesos,
        cada copia sigue la trayectoria que tiene el proceso en el esquema Round Robin, por lo mismo el metodo debe evaluar si el proceso actual segun el indice i es una copia
        de un proceso que ya fue evaluado, si es el caso le reduce el burstTime por 1, de lo contrario significa que es la primera vez que se evalua el proceso y no le reduce el burstTime, esto
        mediante el metodo shouldReduceBurstTime.
        Una variable de suma importancia es la variable burstTimeLeft del objeto process dentro de cada processState ya que lleva el conteo del burstTime que le falta a cada proceso,
        en este caso por cada iteración se le reduce un quantum al tiempo del burstTimeLeft mediante el metodo updateBurstTimeLeft.
        Posteriormente se evalua si el burstTime left es menor o igual a 0, es decir evalua si el proceso fue ejecutado completamente o no, si es asi
        entonces finaliza el proceso principal, osea el primero que tiene el burstTime original y tambien todos los procesos copia de este mediante el metodo handleProcessCompletation,
        si no es asi entonces aumenta el tiempo actual en un quantum y añade una copia del mismo proceso al final de la lista auxiliar mediante el metodo
        handleProcessContinuation. Finalmente aumenta el contador i para evaluar el siguiente proceso en la cola.

        Args:
            quantum (int): Tiempo máximo que cada proceso puede ejecutarse antes de ser interrumpido y enviado a la cola de espera.

        Returns:
            list: La tupla de todos los StateProcess con los procesos ya finalizados y el burstTime respectivo de cada copia de proceso.
        """
        self.currentTime = 0
        self.processStates.sort(key=lambda x: x.arrivalTime)
        processStatesAux = self.initializeProcessStatesAux(quantum)
        self.initialSize = len(processStatesAux)

        i = 0
        while i < len(processStatesAux):
            if self.shouldReduceBurstTime(i, processStatesAux):
                self.reduceBurstTime(processStatesAux[i], quantum)
            elif i == 0:
                self.currentTime = processStatesAux[i].arrivalTime

            self.updateBurstTimeLeft(processStatesAux[i], quantum)

            if processStatesAux[i].process.burstTimeLeft <= 0:
                self.handleProcessCompletion(processStatesAux, i, quantum)
            else:
                self.handleProcessContinuation(processStatesAux, i, quantum)

            i += 1

        return processStatesAux

    def initializeProcessStatesAux(self, quantum):
        """
        Inicializa la lista auxiliar de procesos esta lista auxiliar es la que se va a procesar, si el quantum es mayor a 1 se inicializa con todos los procesos de la tupla processStates,
        si el quantum es menor o igual a 1 se inicializa con los dos primeros procesos de la tupla processStates. Esto se hace con la finalidad de otorgarle prioridad
        a los procesos que llegan a la cola mientras hay procesos reasignados a la cola por cambios de contexto, esto se debe a que si el quantum es 1 hay una gran velocidad
        en los cambios de contexto y esto puede hacer que los nuevos procesos deban esperar mas, por ejemplo:
        Si ingresa el proceso 1 en el tiempo 0, el proceso 2 en el tiempo 1, el proceso 3 en el tiempo 2 y el proceso 4 en el tiempo 3 con un quantum de 1, lo que ocurre es que
        en el tiempo 0 ingresa el proceso 1 y se ejecuta por 1 segundo(quantum), luego en el tiempo 1 ingresa el proceso 2 por lo que el esquema debe retirar al proceso 1
        de la CPU y ejecutar por 1 segundo el proceso 2, en este caso en el tiempo 1 se envia el proceso 1 a la cola de espera de nuevo, luego en el tiempo 2 ingresa el proceso 3, 
        este proceso va a la cola de espera detras del proceso 1, por ende el proceso 1 debe ejecutarse en este segundo durante un quantum y el proceso 2 va a la cola de espera detras
        del proceso 3.
        Entonces la razon por la cual si el quantum es menor o igual a 1 se inicializa la lista auxiliar con los dos primeros procesos de la tupla processStates es para
        poder otorgarle prioridad en el tiempo 2 al proceso 3 sobre el proceso 2, como se puede deducir, ambos procesos van a la cola de espera en el tiempo 2, pero,
        el proceso 2 ya tuvo un quantum de ejecución por lo menos asi que debe priorizarse el nuevo proceso entrante(proceso 3).

        Args:
            quantum (int): Tiempo máximo que cada proceso puede ejecutarse antes de ser interrumpido y enviado a la cola de espera.

        Returns:
            list: Lista inicial de procesos que deben procesarse.
        """
        if quantum > 1:
            return copy.deepcopy(self.processStates)
        else:
            processStatesAux = [copy.deepcopy(self.processStates[0])]
            if len(self.processStates) > 1:
                processStatesAux.append(copy.deepcopy(self.processStates[1]))
            return processStatesAux

    def shouldReduceBurstTime(self, i, processStatesAux):
        """
        Determina si se debe reducir el burst time de un proceso, dependiendo si el proceso es una copia y ya se encuentra en la lista auxiliar,
        con el fin de que las copias del proceso lleven el cambio historico del burstTime en la simulación
        o de lo contrario si es la copia original, en este caso no se le reduce el burstTime.

        Args:
            i (int): Índice del proceso actual en la lista auxiliar.
            processStatesAux (list): Lista auxiliar de procesos.

        Returns:
            bool: True si se debe reducir el burst time, False en caso contrario.
        """
        return i > 0 and (i > (self.initialSize - 1) and self.pidRegisteredInList(processStatesAux, processStatesAux[i].process.pid, i))

    def reduceBurstTime(self, processState, quantum):
        """
        Reduce el burst time de un proceso en un quantum.

        Args:
            processState (StateProcess): Proceso a modificar.
            quantum (int): Tiempo máximo que cada proceso puede ejecutarse antes de ser interrumpido y enviado a la cola de espera.
        """
        processState.process.burstTime -= quantum

    def updateBurstTimeLeft(self, processState, quantum):
        """
        Actualiza el tiempo restante de ejecución de un proceso en la simulación segun el quantum.

        Args:
            processState (StateProcess): Proceso a actualizar.
            quantum (int): Tiempo máximo que cada proceso puede ejecutarse antes de ser interrumpido y enviado a la cola de espera.
        """
        processState.process.burstTimeLeft -= quantum

    def handleProcessCompletion(self, processStatesAux, i, quantum):
        """
        Gestiona la finalizacion de un proceso, para ello determina cual es el proceso principal segun el indice i recorriendo processStatesAux
        y evaluando cual es el primer proceso registrado con el mismo pid, el indice de el proceso encontrado se almacena, luego finaliza el proceso principal.
        Posteriormente vuelve a recorrer todos los demas procesos segun el indice i y evalua cuales coinciden con el pid del proceso principal del indice j, todos los
        procesos copia que se encuentran son finalizados y se le asigna el mismo waitingTime del proceso principal para que halla sincronia entre todos.
        Adiciomalmente, evalua si un nuevo proceso ha ingresado al sistema segun su arrivalTime, si es asi entonces lo añade priorizando añadir este proceso antes que la copia
        del proceso actual mediante el metodo addNewArrivingProcesses.
        Args:
            processStatesAux (list): Lista auxiliar de procesos.
            i (int): Índice del proceso completado.
            quantum (int): Tiempo máximo que cada proceso puede ejecutarse antes de ser interrumpido y enviado a la cola de espera.
        """
        self.currentTime += quantum + processStatesAux[i].process.burstTimeLeft
        processStatesAux[i].process.burstTimeLeft = 0
        processStatesAux[i].finishProcess(self.currentTime)

        firstIndex = None
        for j in range(len(processStatesAux)):
            if j != i and processStatesAux[j].process.pid == processStatesAux[i].process.pid:
                processStatesAux[j].finishProcess(self.currentTime)
                if firstIndex is None:
                    firstIndex = j
                    processStatesAux[i].waitingTime = processStatesAux[firstIndex].waitingTime
                else:
                    processStatesAux[j].waitingTime = processStatesAux[firstIndex].waitingTime

        self.addNewArrivingProcesses(processStatesAux, i)

    def handleProcessContinuation(self, processStatesAux, i, quantum):
        """
        Maneja la continuación de un proceso que no ha terminado, para ello aumenta el tiempo actual en un quantum
        y añade una copia del mismo proceso al final de la lista auxiliar, adiciomalmente, evalua si un nuevo proceso ha ingresado
        al sistema segun su arrivalTime, si es asi entonces lo añade priorizando añadir este proceso antes que la copia
        del proceso actual mediante el metodo addNewArrivingProcesses.

        Args:
            processStatesAux (list): Lista auxiliar de procesos.
            i (int): Índice del proceso actual.
            quantum (int): Tiempo máximo que cada proceso puede ejecutarse antes de ser interrumpido y enviado a la cola de espera.
        """
        self.currentTime += quantum
        self.addNewArrivingProcesses(processStatesAux, i)
        processStatesAux.append(copy.deepcopy(processStatesAux[i]))

    def addNewArrivingProcesses(self, processStatesAux, i):
        """
        Evalua si existen procesos nuevos que ingresan al sistema, en este caso lo que hace es adelantarse en la lista de processStates por 1 unidad
        para poder evaluar si algun proceso en la lista tiene el mismo valor arrivalTime que el tiempo actual del sistema(currentTime),
        ademas tambien evalua si el proceso ya se encuentra en la lista auxiliar para evitar duplicaciones innecesarias, si es asi
        y ya se encuentra un proceso con su mismo pid significa que el proceso ya se encuentra en la lista auxiliar mediante el metodo pidRegisteredInList.

        Args:
            processStatesAux (list): Lista auxiliar de procesos.
            i (int): Índice del proceso actual.
        """
        if i + 1 < len(self.processStates) and (((self.processStates[i + 1].arrivalTime == self.currentTime) and (not self.pidRegisteredInList(processStatesAux, self.processStates[i + 1].process.pid))) or ((self.processStates[i + 1].arrivalTime == self.currentTime + 1) and (not self.pidRegisteredInList(processStatesAux, self.processStates[i + 1].process.pid)))):
            processStatesAux.append(copy.deepcopy(self.processStates[i + 1]))
    
    def runBatch(self):
        """
        Ejecuta el procesamiento por lotes, dividiendo los procesos en lotes y procesándolos en serie.

        Args:
            None

        Returns:
            tuple: Una lista de lotes (cada lote es una lista de procesos) y un diccionario que mapea los PIDs con sus números de lote.
        """
        self.currentTime = 0
        batchSize = 4  
        batches = []
        batchMapping = {} 

        self.processStates.sort(key=lambda x: x.arrivalTime)

        for i in range(0, len(self.processStates), batchSize):
            batch = self.processStates[i:i + batchSize]
            batchNumber = len(batches) + 1  
            for processState in batch:
                batchMapping[processState.process.pid] = batchNumber  
            batches.append(batch)

        for batch in batches:
            for processState in batch:
                if self.currentTime < processState.arrivalTime:
                    self.currentTime = processState.arrivalTime
                self.currentTime += processState.process.burstTime
                processState.finishProcess(self.currentTime)

        return batches, batchMapping  
    
    def pidRegistered(self, pid):
        """
        Verifica si un PID ya está registrado en los procesos principales de processStates.

        Args:
            pid (int): Identificador del proceso a buscar.

        Returns:
            bool: True si el PID ya esta, False en caso contrario.
        """
        for process in self.processStates:
            if process.process.pid == pid:
                return True
        return False
    
    def pidRegisteredInList(self, processStates, pid, index=None):
        """
        Verifica si un PID existe en una lista de procesos en concreto. Opcionalmente permite hacer esta verificación
        ignorando un index en especifico, esto se debe a que puede evaluar si un proceso en particular
        posee copias creadas dentro de la lista processStates, para ello ignora su propia existencia en la lista.

        Args:
            processStates (list): Lista de procesos dada.
            pid (int): Identificador del proceso a buscar.
            index (int, optional): Índice a ignorar en la búsqueda.

        Returns:
            bool: True si el PID existe (excepto en el índice indicado), False en caso contrario.
        """
        for i in range(len(processStates)):
            if processStates[i].process.pid == pid and i != index:
                return True
        return False
    
    def getProcessStates(self):
        """
        Obtiene la lista de estados de procesos ordenados por tiempo de llegada.

        Returns:
            list: Lista de StateProcess ordenados por arrivalTime.
        """
        self.processStates.sort(key=lambda x: x.arrivalTime)
        return self.processStates
