import tkinter as tk
from tkinter import ttk
from tkinter import ttk, messagebox
from IClassesModels import ISerieProcessingView, IBatchProcessingView

class SerieProcessingView(ISerieProcessingView):
    def __init__(self, parent, addProcess, runAnimation):
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True)

        self.columns = ("PID", "AT", "BT", "CT", "TAT", "WT")
        self.table = ttk.Treeview(self.frame, columns=self.columns, show="headings", height=10)
        
        for col in self.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100)
        
        self.table.pack(pady=10)
        
        self.inputFrame = tk.Frame(self.frame)
        self.inputFrame.pack(pady=10)
        
        tk.Label(self.inputFrame, text="PID:").pack(side=tk.LEFT, padx=5)
        self.pid_entry = tk.Entry(self.inputFrame)
        self.pid_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.inputFrame, text="Arrive Time:").pack(side=tk.LEFT, padx=5)
        self.arriveTimeEntry = tk.Entry(self.inputFrame)
        self.arriveTimeEntry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.inputFrame, text="Burst Time:").pack(side=tk.LEFT, padx=5)
        self.burstTimeEntry = tk.Entry(self.inputFrame)
        self.burstTimeEntry.pack(side=tk.LEFT, padx=5)
        
        self.buttonFrame = tk.Frame(self.frame)
        self.buttonFrame.pack(pady=10)

        self.addButton = tk.Button(self.buttonFrame, text="Añadir proceso", command=addProcess)
        self.addButton.pack(side=tk.LEFT, padx=5)

        self.animate_button = tk.Button(self.buttonFrame, text="Ejecutar animacion", command=runAnimation)
        self.animate_button.pack(side=tk.LEFT, padx=5)
        
    def drawAnimation(self, processStates):
        if len(processStates) == 0:
            self.showErrorMessage("Debe añadir minimo un proceso.")
            return
        
        animationWindow = tk.Toplevel(self.frame)
        animationWindow.title("Animación de procesamiento en serie")
        canvas = tk.Canvas(animationWindow, width=800, height=400, bg="white")
        canvas.pack()
        currentTime = 0
        x_start = 50
        yStart = 100
        boxWidth = 100
        boxHeight = 50
        gap = 10

        canvas.create_text(100, 50, text="Waiting", font=("Arial", 14))
        canvas.create_text(400, 50, text="Running", font=("Arial", 14))
        canvas.create_text(700, 50, text="Completed", font=("Arial", 14))

        waitingArea = []
        runningArea = None
        completedArea = []
        
        burstTime = None

        def update_canvas():
            nonlocal currentTime, waitingArea, runningArea, completedArea, burstTime
            
            canvas.delete("process")
            canvas.delete("time")
            
            canvas.create_text(400, 20, text=f"Tiempo actual: {currentTime}", font=("Arial", 16), tag="time")

            for process in processStates:
                if process.arriveTime == currentTime:
                    waitingArea.append(process)

            if not runningArea and waitingArea:
                runningArea = waitingArea.pop(0)
            
            if runningArea:
                
                if burstTime is None:
                    burstTime = runningArea.process.burstTime
                elif burstTime == -1:
                    burstTime = runningArea.process.burstTime - 1
                
                if burstTime == 0:
                    canvas.delete("process")
                    completedArea.append(runningArea)
                    
                    if len(waitingArea) > 0:
                        runningArea = waitingArea.pop(0)
                    else:
                        runningArea = None
                    burstTime = -1
                    
                    
                if burstTime is not None and burstTime > 0:
                    burstTime -= 1
                
                if runningArea is not None:
                    canvas.create_rectangle(
                        350, yStart,
                        350 + boxWidth, yStart + boxHeight,
                        fill="lightgreen", tags="process"
                    )
                    canvas.create_text(
                        350 + boxWidth // 2, yStart + boxHeight // 2,
                        text=f"{runningArea.process.pid}", tags="process"
                    )
            
            for i, process in enumerate(waitingArea):
                canvas.create_rectangle(
                    x_start, yStart + i * (boxHeight + gap),
                    x_start + boxWidth, yStart + i * (boxHeight + gap) + boxHeight,
                    fill="lightblue", tags="process"
                )
                canvas.create_text(
                    x_start + boxWidth // 2, yStart + i * (boxHeight + gap) + boxHeight // 2,
                    text=f"{process.process.pid}", tags="process"
                )  
            
            for i, process in enumerate(completedArea):
                canvas.create_rectangle(
                    650, yStart + i * (boxHeight + gap),
                    650 + boxWidth, yStart + i * (boxHeight + gap) + boxHeight,
                    fill="lightgray", tags="process"
                )
                canvas.create_text(
                    650 + boxWidth // 2, yStart + i * (boxHeight + gap) + boxHeight // 2,
                    text=f"{process.process.pid}", tags="process"
                )

            currentTime += 1

            if runningArea or waitingArea or len(completedArea) < len(processStates):
                canvas.after(1000, update_canvas)

        update_canvas()
    
    def showErrorMessage(self, message):
        messagebox.showerror("Error", message)
    
    def cleanRows(self):
        for row in self.table.get_children():
            self.table.delete(row)
            
    def cleanInputs(self):
        self.arriveTimeEntry.delete(0, tk.END) 
        self.pid_entry.delete(0, tk.END)
        self.burstTimeEntry.delete(0, tk.END)
    
    def addTableValues(self, processStates):
        for state in processStates:
            self.table.insert("", "end", values=state.getValues())

class BatchProcessingView(IBatchProcessingView):
    def __init__(self, parent, addProcess, runAnimation):
        """
        Inicializa la vista de procesamiento por lotes.

        Args:
            parent (tk.Widget): Contenedor padre donde se colocará la vista.
            addProcess (function): Función para añadir un proceso.
            runAnimation (function): Función para ejecutar la animación.

        Returns:
            None
        """
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True)

        self.columns = ("PID", "AT", "BT", "CT", "TAT", "WT")
        self.table = ttk.Treeview(self.frame, columns=self.columns, show="headings", height=10)
        
        for col in self.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100)
        
        self.table.pack(pady=10)
        
        self.inputFrame = tk.Frame(self.frame)
        self.inputFrame.pack(pady=10)
        
        tk.Label(self.inputFrame, text="PID:").pack(side=tk.LEFT, padx=5)
        self.pid_entry = tk.Entry(self.inputFrame)
        self.pid_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.inputFrame, text="Arrive Time:").pack(side=tk.LEFT, padx=5)
        self.arriveTimeEntry = tk.Entry(self.inputFrame)
        self.arriveTimeEntry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.inputFrame, text="Burst Time:").pack(side=tk.LEFT, padx=5)
        self.burstTimeEntry = tk.Entry(self.inputFrame)
        self.burstTimeEntry.pack(side=tk.LEFT, padx=5)
        
        self.buttonFrame = tk.Frame(self.frame)
        self.buttonFrame.pack(pady=10)

        self.addButton = tk.Button(self.buttonFrame, text="Añadir proceso", command=addProcess)
        self.addButton.pack(side=tk.LEFT, padx=5)

        self.animate_button = tk.Button(self.buttonFrame, text="Ejecutar animacion", command=runAnimation)
        self.animate_button.pack(side=tk.LEFT, padx=5)
        
    def drawAnimation(self, processStates, batchMapping):
        """
        Dibuja la animación del procesamiento por lotes.

        Args:
            processStates (list): Lista de estados de los procesos.
            batchMapping (dict): Diccionario que mapea los PIDs con sus números de lote.

        Returns:
            None
        """
        if len(processStates) == 0:
            self.showErrorMessage("Debe añadir mínimo un proceso.")
            return

        animationWindow = tk.Toplevel(self.frame)
        animationWindow.title("Animación de procesamiento por lotes")
        canvas = tk.Canvas(animationWindow, width=800, height=400, bg="white")
        canvas.pack()
        currentTime = 0
        x_start = 50
        yStart = 100
        boxWidth = 100
        boxHeight = 50
        gap = 10

        canvas.create_text(100, 50, text="Waiting", font=("Arial", 14))
        canvas.create_text(400, 50, text="Running", font=("Arial", 14))
        canvas.create_text(700, 50, text="Completed", font=("Arial", 14))

        waitingArea = []
        runningArea = None
        completedArea = []
        burstTime = None

        def getBatchNumber(pid):
            """
            Obtiene el número del lote al que pertenece un proceso.

            Args:
                pid (int): Identificador único del proceso.

            Returns:
                int: Número del lote al que pertenece el proceso.
            """
            return batchMapping.get(pid, "N/A")  

        def update_canvas():
            """
            Actualiza el lienzo de la animación en cada iteración.

            Args:
                None

            Returns:
                None
            """
            nonlocal currentTime, waitingArea, runningArea, completedArea, burstTime

            canvas.delete("process")
            canvas.delete("time")

            canvas.create_text(400, 20, text=f"Tiempo actual: {currentTime}", font=("Arial", 16), tag="time")

            for process in processStates:
                if process.arriveTime == currentTime:
                    waitingArea.append(process)

            if not runningArea and waitingArea:
                runningArea = waitingArea.pop(0)

            if runningArea:
                if burstTime is None:
                    burstTime = runningArea.process.burstTime
                elif burstTime == -1:
                    burstTime = runningArea.process.burstTime - 1

                if burstTime == 0:
                    canvas.delete("process")
                    completedArea.append(runningArea)

                    if len(waitingArea) > 0:
                        runningArea = waitingArea.pop(0)
                    else:
                        runningArea = None
                    burstTime = -1

                if burstTime is not None and burstTime > 0:
                    burstTime -= 1

                if runningArea is not None:
                    batchNumber = getBatchNumber(runningArea.process.pid)  
                    canvas.create_rectangle(
                        350, yStart,
                        350 + boxWidth, yStart + boxHeight,
                        fill="lightgreen", tags="process"
                    )
                    canvas.create_text(
                        350 + boxWidth // 2, yStart + boxHeight // 2,
                        text=f"Lote: {batchNumber}, PID: {runningArea.process.pid}",
                        tags="process"
                    )

            for i, process in enumerate(waitingArea):
                batchNumber = getBatchNumber(process.process.pid)  
                canvas.create_rectangle(
                    x_start, yStart + i * (boxHeight + gap),
                    x_start + boxWidth, yStart + i * (boxHeight + gap) + boxHeight,
                    fill="lightblue", tags="process"
                )
                canvas.create_text(
                    x_start + boxWidth // 2, yStart + i * (boxHeight + gap) + boxHeight // 2,
                    text=f"Lote: {batchNumber}, PID: {process.process.pid}",
                    tags="process"
                )

            for i, process in enumerate(completedArea):
                batchNumber = getBatchNumber(process.process.pid)  
                canvas.create_rectangle(
                    650, yStart + i * (boxHeight + gap),
                    650 + boxWidth, yStart + i * (boxHeight + gap) + boxHeight,
                    fill="lightgray", tags="process"
                )
                canvas.create_text(
                    650 + boxWidth // 2, yStart + i * (boxHeight + gap) + boxHeight // 2,
                    text=f"Lote: {batchNumber}, PID: {process.process.pid}",
                    tags="process"
                )

            currentTime += 1

            if runningArea or waitingArea or len(completedArea) < len(processStates):
                canvas.after(1000, update_canvas)

        update_canvas()
    
    def showErrorMessage(self, message):
        """
        Muestra un mensaje de error en un cuadro de diálogo.

        Args:
            message (str): Mensaje de error a mostrar.

        Returns:
            None
        """
        messagebox.showerror("Error", message)
    
    def cleanRows(self):
        """
        Limpia todas las filas de la tabla de procesos.

        Args:
            None

        Returns:
            None
        """
        for row in self.table.get_children():
            self.table.delete(row)
            
    def cleanInputs(self):
        """
        Limpia los campos de entrada de la vista.

        Args:
            None

        Returns:
            None
        """
        self.arriveTimeEntry.delete(0, tk.END) 
        self.pid_entry.delete(0, tk.END)
        self.burstTimeEntry.delete(0, tk.END)
    
    def addTableValues(self, processStates):
        """
        Añade los valores de los estados de los procesos a la tabla.

        Args:
            processStates (list): Lista de estados de los procesos.

        Returns:
            None
        """
        for state in processStates:
            self.table.insert("", "end", values=state.getValues())


class MainView:
    def __init__(self):
        """
        Inicializa la vista principal con pestañas para procesamiento en serie y por lotes.

        Args:
            None

        Returns:
            None
        """
        self.root = tk.Tk()
        self.root.title("Aplicación con Pestañas")
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.serieProcessingTab = None
        self.batchProcessingTab = None

    def configureSerieProcessingTab(self, serieController):
        """
        Configura la pestaña de procesamiento en serie.

        Args:
            serieController (SerieProcessingController): Controlador para el procesamiento en serie.

        Returns:
            None
        """
        self.serieProcessingTab = SerieProcessingView(
            self.notebook, serieController.addProcess, serieController.runAnimation
        )
        self.notebook.add(self.serieProcessingTab.frame, text="Procesamiento en Serie")

    def configureBatchProcessingTab(self, batchController):
        """
        Configura la pestaña de procesamiento por lotes.

        Args:
            batchController (BatchProcessingController): Controlador para el procesamiento por lotes.

        Returns:
            None
        """
        self.batchProcessingTab = BatchProcessingView(
            self.notebook, batchController.addProcess, batchController.runAnimation
        )
        self.notebook.add(self.batchProcessingTab.frame, text="Procesamiento por Lotes")

    def run(self):
        """
        Inicia el bucle principal de la aplicación.

        Args:
            None

        Returns:
            None
        """
        self.root.mainloop()


class SerieProcessingController:
    def __init__(self, mainView=None):
        self.processManager = ProcessManager()
        self.mainView = mainView

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
        
        self.processManager.addProcess(int(pid), int(arriveTime), int(burstTime))
        self.processManager.runSerie()
        serieView.cleanRows()
        serieView.addTableValues(self.processManager.processStates)
        serieView.cleanInputs()
    
    def runAnimation(self):
        serieView = self.mainView.serieProcessingTab
        serieView.drawAnimation(self.processManager.processStates)

    def configureView(self):
        # Configurar los botones después de que MainView esté inicializado
        self.mainView.serieProcessingTab.addButton.config(command=self.addProcess)
        self.mainView.serieProcessingTab.animate_button.config(command=self.runAnimation)


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

    def addProcess(self):
        """
        Añade un proceso a la lista de procesos del gestor de procesos por lotes.

        Args:
            None (Los valores se obtienen directamente de los campos de entrada en la vista).

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
        
        self.processManager.addProcess(int(pid), int(arriveTime), int(burstTime))
        self.processManager.runSerie()
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
        batchView.drawAnimation(self.processManager.processStates, self.processManager.batchMapping)

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