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
        # Configurar los botones después de que MainView esté inicializado
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


#Procesamiento por lotes
class BatchProcessingController:
    def __init__(self, mainView=None):
        self.processManager = ProcessManager()
        self.mainView = mainView

    def configureView(self):
        # Configurar los botones después de que MainView esté inicializado
        self.mainView.batchProcessingTab.addButton.config(command=self.addProcess)
        self.mainView.batchProcessingTab.animate_button.config(command=self.runAnimation)

    def addProcess(self):
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
            self.processManager.runSerie()
            batchView.cleanRows()
            batchView.addTableValues(self.processManager.processStates)
            batchView.cleanInputs()
    
    def runAnimation(self):
        batchView = self.mainView.batchProcessingTab
        batchView.drawAnimation(self.processManager.processStates)
    
    def run(self):
        self.mainView.run()


# EJECUTA EL CONTROLADOR
if __name__ == "__main__":
    # Crear una instancia de MainView sin controladores
    mainView = MainView()

    # Crear instancias de los controladores
    serieController = SerieProcessingController(mainView)
    batchController = BatchProcessingController(mainView)

    # Configurar las pestañas en MainView
    mainView.configureSerieProcessingTab(serieController)
    mainView.configureBatchProcessingTab(batchController)

    # Configurar las vistas después de inicializar MainView
    serieController.configureView()
    batchController.configureView()

    # Ejecutar la aplicación
    mainView.run()