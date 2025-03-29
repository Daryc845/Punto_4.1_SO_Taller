import tkinter as tk
from tkinter import ttk
from tkinter import ttk, messagebox
from IClassesModels import ISerieProcessingController
from models import ProcessManager
from models import Batch
from views import SerieProcessingView
from views import BatchProcessingView
from models import Process


class SerieProcessingController(ISerieProcessingController):
    def __init__(self):
        self.processManager = ProcessManager()
        self.__serieView = SerieProcessingView(self.addProcess, self.runAnimation)
    
    def addProcess(self):
        pid = self.__serieView.pid_entry.get()
        arriveTime = self.__serieView.arriveTimeEntry.get()
        burstTime = self.__serieView.burstTimeEntry.get()
        
        if not pid.strip():
            self.__serieView.showErrorMessage("El campo PID no puede estar vacío.")
            return
        
        if not arriveTime.strip():
            self.__serieView.showErrorMessage("El campo Arrive Time no puede estar vacío.")
            return
        
        if not burstTime.strip():
            self.__serieView.showErrorMessage("El campo Burst Time no puede estar vacío.")
            return
        
        if not pid.isdigit() or not arriveTime.isdigit() or not burstTime.isdigit():
            self.__serieView.showErrorMessage("Todos los campos deben contener valores numéricos.")
            return
        
        if self.processManager.pidRegistered(int(pid)):
            self.__serieView.showErrorMessage("El PID ya esta registrado, digite otro.")
            return
        
        if arriveTime:
            self.processManager.addProcess(int(pid), int(arriveTime), int(burstTime))
            self.processManager.runSerie()
            self.__serieView.cleanRows()
            self.__serieView.addTableValues(self.processManager.processStates)
            self.__serieView.cleanInputs()
    
    def runAnimation(self):
        self.__serieView.drawAnimation(self.processManager.processStates)
    
    def run(self):
        self.__serieView.root.mainloop()


class BatchProcessingController:
    def __init__(self, view, process_manager):
        self.view = view
        self.process_manager = process_manager
        self.batches = {}

    def add_process_to_batch(self, batch_id, pid, arrive_time, burst_time):
        if batch_id not in self.batches:
            self.batches[batch_id] = Batch(batch_id)

        # Crear el proceso con arrive_time
        process = Process(pid, burst_time, arrive_time)
        self.batches[batch_id].add_process(process)
        self.view.update_batch_table(batch_id, process)

    def execute_batches(self):
        for batch_id, batch in self.batches.items():
            self.process_manager.processes = batch.get_processes()
            self.process_manager.execute_processes()
            self.view.update_batch_execution(batch_id, self.process_manager.states)

#EJECUTA EL CONTROLADOR(ADJUNTAR AQUI TODOS LOS CONTROLADORES)
if __name__ == "__main__":
    # Inicializa la ventana principal de Tkinter
    root = tk.Tk()
    
    # Crea el gestor de procesos
    process_manager = ProcessManager()
    
    # Crea el controlador de procesamiento por lotes
    batch_controller = BatchProcessingController(None, process_manager)
    
    # Crea la vista de procesamiento por lotes y la conecta al controlador
    batch_view = BatchProcessingView(root, batch_controller)
    
    # Actualiza el controlador con la referencia a la vista
    batch_controller.view = batch_view
    
    # Ejecuta el bucle principal de la interfaz gráfica
    batch_view.mainloop()


