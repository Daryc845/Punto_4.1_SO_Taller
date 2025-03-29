import tkinter as tk
from tkinter import ttk
from tkinter import ttk, messagebox
from models import ProcessManager
from views import MainView


class SerieProcessingController:
    def __init__(self):
        self.processManager = ProcessManager()
        self.mainView = MainView()

        # Conectar métodos de la pestaña de procesamiento en serie
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

# EJECUTA EL CONTROLADOR
if __name__ == "__main__":
    serieProcessingController = SerieProcessingController()
    serieProcessingController.run()