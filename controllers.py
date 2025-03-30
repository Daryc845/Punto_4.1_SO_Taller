import tkinter as tk
from tkinter import ttk
from tkinter import ttk, messagebox
from batchMultiprocessing import BatchMultiProcessingView
from models import ProcessManager
from IClassesModels import ISerieProcessingController
from views import SerieProcessingView, TimeshareProcessingView, MainView
import copy


class SerieProcessingController(ISerieProcessingController):
    def __init__(self, mainView=None):
        """
        Construye un objeto SerieProcessingController, este objeto gestiona la relacion del modelo con la vista,
        basicamente funciona como el controlador del administrador de tareas segun el esquema de procesamiento en serie.
        Para esto inicializa un objeto vista(serieView) pasandole por parametro metodos del controlador necesarios y
        un objeto modelo(processManager)
        """
        self.processManager = ProcessManager()
        self.mainView = mainView
    
    def addProcess(self):
        """
        Gestiona el evento de añadir un proceso, para ello evalua si los campos de ingreso, no estan vacios, tienen unicamente
        numeros validos ingresados(enteros, mayores que 1) y no tienen otros tipos de caracteres, en caso contrario genera avisos con
        el metodo showErrorMessage de serieView, luego ejecuta la simulación con runSerie del processManager y actualiza la vista con addTableValues() de serieView
        """
        serieView = self.mainView.serieProcessingTab
        pid = serieView.pid_entry.get()
        arrivalTime = serieView.arrivalTimeEntry.get()
        burstTime = serieView.burstTimeEntry.get()
        
        if not pid.strip():
            serieView.showErrorMessage("El campo PID no puede estar vacío.")
            return
        
        if not arrivalTime.strip():
            serieView.showErrorMessage("El campo Arrive Time no puede estar vacío.")
            return
        
        if not burstTime.strip():
            serieView.showErrorMessage("El campo Burst Time no puede estar vacío.")
            return
        
        if not pid.isdigit() or not arrivalTime.isdigit() or not burstTime.isdigit():
            serieView.showErrorMessage("Todos los campos deben contener valores numéricos.")
            return
        
        if self.processManager.pidRegistered(int(pid)):
            serieView.showErrorMessage("El PID ya esta registrado, digite otro.")
            return
        
        if arrivalTime:
            self.processManager.addProcess(int(pid), int(arrivalTime), int(burstTime))
            self.processManager.runSerie()
            serieView.cleanRows()
            serieView.addTableValues(self.processManager.processStates)
            serieView.cleanInputs()
        
        def run(self):
            """
            Inicia la ejecución de la vista principal.

            Args:
                None

            Returns:
                None
            """
            self.mainView.run()
    
    def runAnimation(self):
        """
        Gestiona el evento de ver animación, para ello hace un llamado al metodo draw animation de serieView.
        """
        serieView = self.mainView.serieProcessingTab
        serieView.drawAnimation(self.processManager.processStates)
    
    def configureView(self):
        # Configurar los botones después de que MainView esté inicializado
        self.mainView.serieProcessingTab.addButton.config(command=self.addProcess)
        self.mainView.serieProcessingTab.animate_button.config(command=self.runAnimation)
        
class TimeshareProcessingController(ISerieProcessingController):
    def __init__(self, mainView=None):
        """
        Construye un objeto TimeshareProcessingController, este objeto gestiona la relacion del modelo con la vista,
        basicamente funciona como el controlador del administrador de tareas segun el esquema de procesamiento en tiempo compartido.
        Para esto inicializa un objeto vista(shareView) pasandole por parametro metodos del controlador necesarios y
        un objeto modelo(processManager)
        """
        self.processManager = ProcessManager()
        self.mainView = mainView
        #shareView = TimeshareProcessingView(self.addProcess, self.runAnimation, self.updateTable)
    
    def addProcess(self):
        """
        Gestiona el evento de añadir un proceso, para ello evalua si los campos de ingreso, no estan vacios, tienen unicamente
        numeros validos ingresados(mayores que 0) y no tienen otros tipos de caracteres, en caso contrario genera avisos con
        el metodo showErrorMessage de shareView, luego ejecuta la simulación con runRoundRobin del processManager y actualiza la vista con addTableValues() de shareView
        """
        shareView = self.mainView.timeshareProcessingTab
        pid = shareView.pid_entry.get()
        arrivalTime = shareView.arrivalTimeEntry.get()
        burstTime = shareView.burstTimeEntry.get()
        quantum = shareView.quantumEntry.get()
        
        if not pid.strip():
            shareView.showErrorMessage("El campo PID no puede estar vacío.")
            return
        
        if not arrivalTime.strip():
            shareView.showErrorMessage("El campo Arrive Time no puede estar vacío.")
            return
        
        if not burstTime.strip():
            shareView.showErrorMessage("El campo Burst Time no puede estar vacío.")
            return
        
        if not quantum.strip():
            shareView.showErrorMessage("El campo Quantum no puede estar vacío.")
            return
        
        if not pid.isdigit() or not arrivalTime.isdigit() or not burstTime.isdigit() or not quantum.isdigit():
            shareView.showErrorMessage("Todos los campos deben contener valores numéricos.")
            return
        
        if int(quantum) < 0:
            shareView.showErrorMessage("El campo Quantum debe ser mayor a 0.")
            return
        
        if self.processManager.pidRegistered(int(pid)):
            shareView.showErrorMessage("El PID ya esta registrado, digite otro.")
            return
        
        self.processManager.addProcess(int(pid), int(arrivalTime), int(burstTime))
        shareView.cleanRows()
        shareView.addTableValues(self.processManager.runRoundRobin(int(quantum)))
        shareView.cleanInputs()
    
    def runAnimation(self):
        """
        Gestiona el evento de ver animación, para ello evalua que el campo quantum no este vacio, tenga un numero valido(mayor que 0)
        y que no tenga otros tipos de caracteres, de lo contrario genera avisos usando el metodo showErrorMessage de shareView, si todo esta bien
        hace un llamado al metodo draw animation de shareView.
        """
        shareView = self.mainView.timeshareProcessingTab
        quantum = shareView.quantumEntry.get()
        if not quantum.strip():
            shareView.showErrorMessage("El campo Quantum no puede estar vacío.")
            return
        if not quantum.isdigit():
            shareView.showErrorMessage("El campo Quantum debe ser un número.")
            return
        if int(quantum) < 0:
            shareView.showErrorMessage("El campo Quantum debe ser mayor a 0.")
            return
        shareView.drawAnimation(copy.deepcopy(self.processManager.processStates), (int(quantum)))
    
    def updateTable(self):
        """
        Gestiona el evento de actualizar la tabla de procesos de la vista, para ello evalua que el campo quantum no este vacio, tenga un numero valido(mayor que 0)
        y que no tenga otros tipos de caracteres, tambien evalua que hallan procesos registrados en processManager, de lo contrario genera avisos usando el metodo 
        showErrorMessage de shareView, luego ejecuta la simulación con runRoundRobin del processManager y actualiza la vista con addTableValues() de shareView
        """
        shareView = self.mainView.timeshareProcessingTab
        quantum = shareView.quantumEntry.get()
        
        if not quantum.strip():
            shareView.showErrorMessage("El campo Quantum no puede estar vacío.")
            return
        
        if len(self.processManager.processStates) == 0:
            shareView.showErrorMessage("No hay procesos registrados.")
            return  
        
        elif not quantum.isdigit():
            shareView.showErrorMessage("Todos los campos deben contener valores numéricos.")
            return
        
        shareView.cleanRows()
        shareView.addTableValues(self.processManager.runRoundRobin(int(quantum)))
        shareView.cleanInputs()
    
    
    def configureView(self):
        # Configurar los botones después de que MainView esté inicializado
        self.mainView.timeshareProcessingTab.addButton.config(command=self.addProcess)
        self.mainView.timeshareProcessingTab.animate_button.config(command=self.runAnimation)
        self.mainView.timeshareProcessingTab.updateButton.config(command=self.updateTable)

    def run(self):
        """
        Inicia la ejecución de la vista principal.

        Args:
            None

        Returns:
            None
        """
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
        arrivalTime = batchView.arrivalTimeEntry.get()
        burstTime = batchView.burstTimeEntry.get()
        
        if not pid.strip():
            batchView.showErrorMessage("El campo PID no puede estar vacío.")
            return
        
        if not arrivalTime.strip():
            batchView.showErrorMessage("El campo Arrive Time no puede estar vacío.")
            return
        
        if not burstTime.strip():
            batchView.showErrorMessage("El campo Burst Time no puede estar vacío.")
            return
        
        if not pid.isdigit() or not arrivalTime.isdigit() or not burstTime.isdigit():
            batchView.showErrorMessage("Todos los campos deben contener valores numéricos.")
            return
        
        if self.processManager.pidRegistered(int(pid)):
            batchView.showErrorMessage("El PID ya está registrado, digite otro.")
            return
        
        if arrivalTime:
            self.processManager.addProcess(int(pid), int(arrivalTime), int(burstTime))
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
    timeshareController = TimeshareProcessingController(mainView)
    batchController = BatchProcessingController(mainView)
    #simulationFrame = BatchMultiProcessingView(mainView.root)

    mainView.configureSerieProcessingTab(serieController)
    mainView.configureTimeshareProcessingTab(timeshareController)
    mainView.configureBatchProcessingTab(batchController)
    mainView.configureBatchMultiProcessingTab()

    serieController.configureView()
    timeshareController.configureView()
    batchController.configureView()

    mainView.run()