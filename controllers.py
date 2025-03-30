import tkinter as tk
from tkinter import ttk
from tkinter import ttk, messagebox
from models import ProcessManager
from IClassesModels import ISerieProcessingController
from views import SerieProcessingView, TimeshareProcessingView, MainView
import copy


class SerieProcessingController(ISerieProcessingController):
    def __init__(self):
        """
        Construye un objeto SerieProcessingController, este objeto gestiona la relacion del modelo con la vista,
        basicamente funciona como el controlador del administrador de tareas segun el esquema de procesamiento en serie.
        Para esto inicializa un objeto vista(serieView) pasandole por parametro metodos del controlador necesarios y
        un objeto modelo(processManager)
        """
        self.processManager = ProcessManager()
        self.serieView = SerieProcessingView(self.addProcess, self.runAnimation)
    
    def addProcess(self):
        """
        Gestiona el evento de añadir un proceso, para ello evalua si los campos de ingreso, no estan vacios, tienen unicamente
        numeros validos ingresados(enteros, mayores que 1) y no tienen otros tipos de caracteres, en caso contrario genera avisos con
        el metodo showErrorMessage de serieView, luego ejecuta la simulación con runSerie del processManager y actualiza la vista con addTableValues() de serieView
        """
        pid = self.serieView.pid_entry.get()
        arrivalTime = self.serieView.arrivalTimeEntry.get()
        burstTime = self.serieView.burstTimeEntry.get()
        
        if not pid.strip():
            self.serieView.showErrorMessage("El campo PID no puede estar vacío.")
            return
        
        if not arrivalTime.strip():
            self.serieView.showErrorMessage("El campo Arrive Time no puede estar vacío.")
            return
        
        if not burstTime.strip():
            self.serieView.showErrorMessage("El campo Burst Time no puede estar vacío.")
            return
        
        if not pid.isdigit() or not arrivalTime.isdigit() or not burstTime.isdigit():
            self.serieView.showErrorMessage("Todos los campos deben contener valores numéricos.")
            return
        
        if self.processManager.pidRegistered(int(pid)):
            self.serieView.showErrorMessage("El PID ya esta registrado, digite otro.")
            return
        
        if arrivalTime:
            self.processManager.addProcess(int(pid), int(arrivalTime), int(burstTime))
            self.processManager.runSerie()
            self.serieView.cleanRows()
            self.serieView.addTableValues(self.processManager.processStates)
            self.serieView.cleanInputs()
    
    def runAnimation(self):
        """
        Gestiona el evento de ver animación, para ello hace un llamado al metodo draw animation de serieView.
        """
        self.serieView.drawAnimation(self.processManager.processStates)
    
    def run(self):
        """
        Ejecuta la interfaz de serieView.
        """
        self.serieView.root.mainloop()
        
class TimeshareProcessingController(ISerieProcessingController):
    def __init__(self):
        """
        Construye un objeto TimeshareProcessingController, este objeto gestiona la relacion del modelo con la vista,
        basicamente funciona como el controlador del administrador de tareas segun el esquema de procesamiento en tiempo compartido.
        Para esto inicializa un objeto vista(shareView) pasandole por parametro metodos del controlador necesarios y
        un objeto modelo(processManager)
        """
        self.processManager = ProcessManager()
        self.shareView = TimeshareProcessingView(self.addProcess, self.runAnimation, self.updateTable)
    
    def addProcess(self):
        """
        Gestiona el evento de añadir un proceso, para ello evalua si los campos de ingreso, no estan vacios, tienen unicamente
        numeros validos ingresados(mayores que 0) y no tienen otros tipos de caracteres, en caso contrario genera avisos con
        el metodo showErrorMessage de shareView, luego ejecuta la simulación con runRoundRobin del processManager y actualiza la vista con addTableValues() de shareView
        """
        pid = self.shareView.pid_entry.get()
        arrivalTime = self.shareView.arrivalTimeEntry.get()
        burstTime = self.shareView.burstTimeEntry.get()
        quantum = self.shareView.quantumEntry.get()
        
        if not pid.strip():
            self.shareView.showErrorMessage("El campo PID no puede estar vacío.")
            return
        
        if not arrivalTime.strip():
            self.shareView.showErrorMessage("El campo Arrive Time no puede estar vacío.")
            return
        
        if not burstTime.strip():
            self.shareView.showErrorMessage("El campo Burst Time no puede estar vacío.")
            return
        
        if not quantum.strip():
            self.shareView.showErrorMessage("El campo Quantum no puede estar vacío.")
            return
        
        if not pid.isdigit() or not arrivalTime.isdigit() or not burstTime.isdigit() or not quantum.isdigit():
            self.shareView.showErrorMessage("Todos los campos deben contener valores numéricos.")
            return
        
        if int(quantum) < 0:
            self.shareView.showErrorMessage("El campo Quantum debe ser mayor a 0.")
            return
        
        if self.processManager.pidRegistered(int(pid)):
            self.shareView.showErrorMessage("El PID ya esta registrado, digite otro.")
            return
        
        self.processManager.addProcess(int(pid), int(arrivalTime), int(burstTime))
        self.shareView.cleanRows()
        self.shareView.addTableValues(self.processManager.runRoundRobin(int(quantum)))
        self.shareView.cleanInputs()
    
    def runAnimation(self):
        """
        Gestiona el evento de ver animación, para ello evalua que el campo quantum no este vacio, tenga un numero valido(mayor que 0)
        y que no tenga otros tipos de caracteres, de lo contrario genera avisos usando el metodo showErrorMessage de shareView, si todo esta bien
        hace un llamado al metodo draw animation de shareView.
        """
        quantum = self.shareView.quantumEntry.get()
        if not quantum.strip():
            self.shareView.showErrorMessage("El campo Quantum no puede estar vacío.")
            return
        if not quantum.isdigit():
            self.shareView.showErrorMessage("El campo Quantum debe ser un número.")
            return
        if int(quantum) < 0:
            self.shareView.showErrorMessage("El campo Quantum debe ser mayor a 0.")
            return
        self.shareView.drawAnimation(copy.deepcopy(self.processManager.processStates), (int(quantum)))
    
    def updateTable(self):
        """
        Gestiona el evento de actualizar la tabla de procesos de la vista, para ello evalua que el campo quantum no este vacio, tenga un numero valido(mayor que 0)
        y que no tenga otros tipos de caracteres, tambien evalua que hallan procesos registrados en processManager, de lo contrario genera avisos usando el metodo 
        showErrorMessage de shareView, luego ejecuta la simulación con runRoundRobin del processManager y actualiza la vista con addTableValues() de shareView
        """
        quantum = self.shareView.quantumEntry.get()
        
        if not quantum.strip():
            self.shareView.showErrorMessage("El campo Quantum no puede estar vacío.")
            return
        
        if len(self.processManager.processStates) == 0:
            self.shareView.showErrorMessage("No hay procesos registrados.")
            return  
        
        elif not quantum.isdigit():
            self.shareView.showErrorMessage("Todos los campos deben contener valores numéricos.")
            return
        
        self.shareView.cleanRows()
        self.shareView.addTableValues(self.processManager.runRoundRobin(int(quantum)))
        self.shareView.cleanInputs()
    
    def run(self):
        """
        Ejecuta la interfaz de serieView.
        """
        self.shareView.root.mainloop()

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