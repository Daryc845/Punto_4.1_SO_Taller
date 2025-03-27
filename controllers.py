import tkinter as tk
from tkinter import ttk
from tkinter import ttk, messagebox
from IClassesModels import ISerieProcessingController
from models import ProcessManager
from views import SerieProcessingView


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
            self.processManager.run()
            self.__serieView.cleanRows()
            self.__serieView.addTableValues(self.processManager.processStates)
            self.__serieView.cleanInputs()
    
    def runAnimation(self):
        self.__serieView.drawAnimation(self.processManager.processStates)
    
    def run(self):
        self.__serieView.root.mainloop()

#EJECUTA EL CONTROLADOR(ADJUNTAR AQUI TODOS LOS CONTROLADORES)
if __name__ == "__main__":
    serieProcessingController = SerieProcessingController()
    serieProcessingController.run()