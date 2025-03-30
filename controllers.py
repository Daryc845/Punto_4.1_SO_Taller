import tkinter as tk
from tkinter import ttk
from tkinter import ttk, messagebox
from models import ProcessManager
from views import MainView


class SerieProcessingController:
    def __init__(self, mainView=None):
        self.processManager = ProcessManager()
        self.mainView = mainView

    def configureView(self):
        self.mainView.serieProcessingTab.addButton.config(command=self.addProcess)
        self.mainView.serieProcessingTab.animate_button.config(command=self.runAnimation)

    def addProcess(self):
        serieView = self.mainView.serieProcessingTab
        pid = serieView.pid_entry.get()
        arriveTime = serieView.arriveTimeEntry.get()
        burstTime = serieView.burstTimeEntry.get()
        
        if not pid.strip():
            serieView.showErrorMessage("El campo PID no puede estar vacío.")
            return
        
        if not arriveTime.strip():
            serieView.showErrorMessage("El campo Arrive Time no puede estar vacío.")
            return
        
        if not burstTime.strip():
            serieView.showErrorMessage("El campo Burst Time no puede estar vacío.")
            return
        
        if not pid.isdigit() or not arriveTime.isdigit() or not burstTime.isdigit():
            serieView.showErrorMessage("Todos los campos deben contener valores numéricos.")
            return
        
        if self.processManager.pidRegistered(int(pid)):
            serieView.showErrorMessage("El PID ya está registrado, digite otro.")
            return
        
        if arriveTime:
            self.processManager.addProcess(int(pid), int(arriveTime), int(burstTime))
            self.processManager.runSerie()
            serieView.cleanRows()
            serieView.addTableValues(self.processManager.processStates)
            serieView.cleanInputs()
    
    def runAnimation(self):
        serieView = self.mainView.serieProcessingTab
        serieView.drawAnimation(self.processManager.processStates)
    
    def run(self):
        self.mainView.run()

class BatchProcessingController:
    def __init__(self, mainView=None):
        """
        Inicializa el controlador de procesamiento por lotes.

        Args:
            mainView (MainView): Instancia de la vista principal que contiene las pestañas de procesamiento.

        Returns:
            None
        """
        self.processManager = ProcessManager()
        self.mainView = mainView

    def configureView(self):
        """
        Configura los botones de la vista de procesamiento por lotes para que ejecuten las acciones correspondientes.

        Args:
            None

        Returns:
            None
        """

        self.mainView.batchProcessingTab.addButton.config(command=self.addProcess)
        self.mainView.batchProcessingTab.animate_button.config(command=self.runAnimation)

    def addProcess(self):
        """
        Añade un proceso a la lista de procesos del gestor de procesos por lotes.

        Args:
            None

        Returns:
            None
        """
        batchView = self.mainView.batchProcessingTab
        pid = batchView.pid_entry.get()
        arriveTime = batchView.arriveTimeEntry.get()
        burstTime = batchView.burstTimeEntry.get()
        
        if not pid.strip():
            batchView.showErrorMessage("El campo PID no puede estar vacío.")
            return
        
        if not arriveTime.strip():
            batchView.showErrorMessage("El campo Arrive Time no puede estar vacío.")
            return
        
        if not burstTime.strip():
            batchView.showErrorMessage("El campo Burst Time no puede estar vacío.")
            return
        
        if not pid.isdigit() or not arriveTime.isdigit() or not burstTime.isdigit():
            batchView.showErrorMessage("Todos los campos deben contener valores numéricos.")
            return
        
        if self.processManager.pidRegistered(int(pid)):
            batchView.showErrorMessage("El PID ya está registrado, digite otro.")
            return
        
        if arriveTime:
            self.processManager.addProcess(int(pid), int(arriveTime), int(burstTime))
            self.processManager.runBatch()
            batchView.cleanRows()
            batchView.addTableValues(self.processManager.processStates)
            batchView.cleanInputs()
    
    def runAnimation(self):
        """
        Ejecuta la animación del procesamiento por lotes, mostrando visualmente el estado de los procesos.

        Args:
            None (Los datos de los procesos y el mapeo de lotes se obtienen del gestor de procesos).

        Returns:
            None
        """ 
        batchView = self.mainView.batchProcessingTab
        _, batchMapping = self.processManager.runBatch()  
        batchView.drawAnimation(self.processManager.processStates, batchMapping)  
    
    def run(self):
        """
        Inicia la ejecución de la vista principal.

        Args:
            None

        Returns:
            None
        """
        self.mainView.run()


if __name__ == "__main__":
    mainView = MainView()

    serieController = SerieProcessingController(mainView)
    batchController = BatchProcessingController(mainView)

    mainView.configureSerieProcessingTab(serieController)
    mainView.configureBatchProcessingTab(batchController)

    serieController.configureView()
    batchController.configureView()

    mainView.run()