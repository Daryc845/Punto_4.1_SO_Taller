import copy
import tkinter as tk
from tkinter import ttk
from tkinter import ttk, messagebox
from batchMultiprocessing import BatchMultiProcessingView
from IClassesModels import ISerieProcessingView, IBatchProcessingView
from models import ProcessManager

class SerieProcessingView(ISerieProcessingView):
    def __init__(self, parent, addProcess, runAnimation):
        """
        Construye un objeto SerieProcessingView, este objeto permite gestionar la interfaz del programa de simulación,
        para ello define una estructura visual primero definiendo el tamaño y proporciones de la ventana principal, luego 
        inicializa una tabla que representara la simulación de una lista de procesos, esta tabla tendra las siguientes columnas:
        PID: el id del proceso
        AT: el tiempo de llegada del proceso
        BT: el tiempo que requiere el proceso para ejecutarse
        CT: el tiempo en el que el proceso terminó de ejecutarse
        TAT: el tiempo transcurrido del proceso desde su primera ejecución hasta cuando termino su ejecución.
        WT: el tiempo que estuvo el proceso en la cola de espera
        Las filas de la tabla representan los procesos, en estas filas se mostrara la información de los mismos.
        Ademas de la tabla se inicializan otros componentes, como botones para poder interactuar con la interfaz mediante
        eventos de click, por ende se añade un boton para el evento de añadir proceso y otro boton para el evento de ejecutar
        animación y tambien campos de entrada(inputs) para recibir los datos necesarios como el PID, el ArrivalTime y
        el BurstTime y almacenarlos hasta cuando se requieran mediante eventos de teclado.
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
        
        tk.Label(self.inputFrame, text="Arrival Time:").pack(side=tk.LEFT, padx=5)
        self.arrivalTimeEntry = tk.Entry(self.inputFrame)
        self.arrivalTimeEntry.pack(side=tk.LEFT, padx=5)
        
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
        """
        Ejecuta una animación en una ventana secundaria, primero evaluando si hay por lo menos 1 proceso en processStates, de lo contrario manda un aviso de error y no permite
        mostrar la animación, esta animación representa el procesamiento segun el esquema en serie para los procesos de 
        processStates dados, para ello utiliza un objeto canvas, este objeto permite renderizar y hacer graficos, es el que permite hacer la animación. Primero, inicializa 
        los valores predeterminados de la ventana como sus proporciones mediante el metodo createAnimationWindow. Luego de esto, compienza la animación, esta animación 
        maneja la logica en serie representando cada proceso como un cuadrado con su PID dibujado en el centro, el conteo de la ejecución la maneja la variable currentTime, tambien
        esta variable se ira actualizando cada segundo por una unidad tambien mediante el metodo drawCurrent time se representa el tiempo actual graficamente segun currentTime y asignandole un tag, 
        el panel se divide en 3 columnas iguales la primera columna con el texto Waiting contendra en su interior los procesos(cuadrados) que se encuentran esperando por tiempo en la CPU,
        la segunda columna con el texto Running contendra el unico proceso que se ejecuta en un determinado momento y la tercera columna con el texto Completed
        contendra a aquellos procesos cuyo BurstTime(Tiempo de rafaga) ya se acabo, es decir fueron ejecutados por completo,
        a todos los cuadrados les asigna un tag, esto es para manipular los elementos con mayor facilidad, esto a nivel visual, a nivel
        logico hay una lista llamada waitingArea que almacena todos los procesos que actualmente se encuentran esperando, tambien un objeto RunningArea
        que sera el proceso que actualmente se encuentra ejecutandose y una lista llamada completedArea que almacena todos los procesos que fueron ejecutados
        completamente. En cada segundo de ejecución se dibujan los procesos de las 3 areas(waiting, running y completed), este dibujo se realiza
        dependiendo de los procesos que se encuentren en cada area, para dibujar y manejar la logica del proceso que se encuentra ejecutandose se usa el metodo
        processRunningProcess, para dibujar los procesos que esten en el area de waiting se usa el metodo drawWaitingArea y para dibujar
        los procesos que se encuentren en el area de Completed se usa el metodo drawCompletedArea.
        Entonces en la primera iteración de la animación se añaden todos los procesos en el area de waiting mediante el metodo addArrivingProcesses,
        luego se evalua si hay algun proceso en waitingArea o no hay en runningArea, en tal caso elimina el primer proceso en el area de waiting
        y lo asigna en el area de running, es decir pasa de estar en espera a ejecutarse. Posterior a esto ejecuta todo el proceso en concreto, asi que
        asigna el runningArea como el proximo proceso en el area de waiting y elimina este proceso del area de waiting y añade el proceso ejecutado en el area de 
        completed mediante el metodo processRunningProcess, luego de esto se dibujan los procesos en waiting
        y los de completed, aumenta el contador currentTime y hace que la animación dure 1 segundo hasta continuar su siguiente iteracion mediante el
        metodo after del objeto canvas. En la siguiente iteración se limpia el canvas con el metodo clearCanvas, esto elimina los cuadrados de procesos y
        el label de tiempo, lo que permite actualizarlos usando los tags de estos elementos. Esto sucesivamente hasta que no halla ningun proceso ni en
        el area de waiting ni en la de running, esto significa que el procesamiento termino, en este punto el currentTime se detiene.
        Args:
            processStates (list): Lista de procesos.
        """
        if len(processStates) == 0:
            self.showErrorMessage("Debe añadir mínimo un proceso.")
            return
        
        animationWindow = tk.Toplevel(self.frame)
        animationWindow.title("Animación de procesamiento en serie")
        canvas = tk.Canvas(animationWindow, width=800, height=400, bg="white")
        canvas.pack()
        currentTime = 0
        x_start, yStart, boxWidth, boxHeight, gap = 50, 100, 100, 50, 10

        self.drawStaticLabels(canvas)

        waitingArea = []
        runningArea = None
        completedArea = []

        burstTime = None

        def update_canvas():
            nonlocal currentTime, waitingArea, runningArea, completedArea, burstTime

            self.clearCanvas(canvas)
            self.drawCurrentTime(canvas, currentTime)

            self.addArrivingProcesses(processStates, waitingArea, currentTime)

            if not runningArea and waitingArea:
                runningArea = waitingArea.pop(0)

            runningArea, burstTime = self.processRunningProcess(canvas, runningArea, waitingArea, completedArea, burstTime, yStart, boxWidth, boxHeight)

            self.drawWaitingArea(canvas, waitingArea, x_start, yStart, boxWidth, boxHeight, gap)
            self.drawCompletedArea(canvas, completedArea, yStart, boxWidth, boxHeight, gap)

            currentTime += 1

            if runningArea or waitingArea or len(completedArea) < len(processStates):
                canvas.after(1000, update_canvas)

        update_canvas()

    def createAnimationWindow(self):
        """
        Inicializa los valores predeterminados de la ventana secundaria de la animación, asignandole los valores del tamaño de la ventana,
        nombre de la ventana, adicionalmente inicializa un canvas, este canvas permite hacer representaciones
        dinamicas de elementos visuales en la pantalla, le especifica sus proporciones, lo añade en la ventana principal de la animación
        y finalmente asigna el canvas a la ventana con el metodo pack.
        
        Returns:
            TopLevel: La ventana secundaria.
            Canvas: El contenedor canvas.
        """
        animationWindow = tk.Toplevel(self.root)
        animationWindow.title("Animación de procesamiento en serie")
        canvas = tk.Canvas(animationWindow, width=800, height=400, bg="white")
        canvas.pack()
        return animationWindow, canvas

    def drawStaticLabels(self, canvas):
        """
        Dibuja los 3 labels pertenecientes a cada area de procesos(waiting, running y completed) en el canvas
        
        Args:
            canvas (Canvas): El canvas correspondiente a actualizar.
        """
        canvas.create_text(100, 50, text="Waiting", font=("Arial", 14))
        canvas.create_text(400, 50, text="Running", font=("Arial", 14))
        canvas.create_text(700, 50, text="Completed", font=("Arial", 14))

    def clearCanvas(self, canvas):
        """
        Limpia los dibujos del canvas pertenecientes al tag process(los procesos) y al tag time(el tiempo actual)
        
        Args:
            canvas (Canvas): El canvas correspondiente a actualizar.
        """
        canvas.delete("process")
        canvas.delete("time")

    def drawCurrentTime(self, canvas, currentTime):
        """
        Dibuja el valor de currentTime en el canvas
                
        Args:
            canvas (Canvas): El canvas correspondiente a actualizar.
            currentTime (int): El tiempo actual.
        """
        canvas.create_text(400, 20, text=f"Tiempo actual: {currentTime}", font=("Arial", 16), tag="time")

    def addArrivingProcesses(self, processStates, waitingArea, currentTime):
        """
        Añade los procesos en la lista de llegada processStates en el area de waiting cuyo arrivalTime es igual al currentTime(llegaron a la cola de espera), 
        para ello recorre todos los procesos de processStates y evalua si el arrivalTime de cada proceso es igual al currentTime,
        si ese es el caso añade el proceso al area de waiting, de lo contrario no.
                
        Args:
            processStates (list): Lista de procesos.
            waitingArea (list): La lista del area de waiting.
            currentTime (int): El tiempo actual.
        """
        for process in processStates:
            if process.arrivalTime == currentTime:
                waitingArea.append(process)

    def processRunningProcess(self, canvas, runningArea, waitingArea, completedArea, burstTime, yStart, boxWidth, boxHeight):
        """
        Gestiona la ejecución del proceso en el area de running, para ello primero evalua si el area de running es diferente de None,
        si es asi entonces significa que hay un proceso ejecutandose, luego evalua si el burstTime es None, el burstTime es None en
        la primera ejecución de algun programa, en este caso le asigna al burstTime el burstTime del proceso en el area de running,
        tambien evalua si el burstTime es igual a -1, este llega a ser igual a -1 cuando hubo antes un proceso que fue ejecutado, en este caso
        para sincronizar el burstTime con el tiempo actual(currentTime) se le asigna el burstTime del proceso en el area de running - 1.
        Posteriormente evalua si el burstTime es igual a 1, si es asi añade el proceso al area de completed y
        lo elimina del runningArea, luego asigna en el area de running al primer proceso del area de waiting pero
        unicamente si waitingArea es difernente de None, es decir aun hay procesos en espera, de lo contrario lo asigna como None,
        cuando esto ocurre significa que la animación debe terminar porque no hay procesos ni en waiting ni en running y reduce en 1
        segundo el burstTime actual para sincronizarlo con el currentTime. Finalmente luego reduce en un segundo el burstTime actual.
                
        Args:
            canvas (Canvas): El canvas correspondiente a actualizar.
            runningArea (ProcessState): El proceso del area de Running.
            waitingArea (list): La lista del area de waiting.
            completedArea (list): La lista del area de completed.
            burstTime (int): El tiempo de rafaga actual.
            y_start (int): La posición y inicial donde empezara el dibujo del cuadrado
            boxWidth (int): El tamaño del ancho del dibujo en pixeles
            boxHeight (int): El tamaño del alto del dibujo en pixeles
        
        Returns:
            runningArea (ProcessState): El proceso que se encuentra en el area de running.
            burstTime (int): El tiempo de rafaga actual.
        """
        if runningArea:
            if burstTime is None:
                burstTime = runningArea.process.burstTime
            elif burstTime == -1:
                burstTime = runningArea.process.burstTime - 1

            if burstTime == 0:
                completedArea.append(runningArea)
                runningArea = waitingArea.pop(0) if waitingArea else None
                burstTime = -1
            else:
                burstTime -= 1

            if runningArea is not None:
                self.drawRunningProcess(canvas, runningArea, yStart, boxWidth, boxHeight)

        return runningArea, burstTime

    def drawRunningProcess(self, canvas, runningArea, yStart, boxWidth, boxHeight):
        """
        Dibuja el proceso del area de running como cuadrado teniendo en cuenta runningArea, para ello le asigna a los 
        cuadrados un tamaño, un tag para identificarlos y los añade al canvas.
                
        Args:
            canvas (Canvas): El canvas correspondiente a actualizar.
            runningArea (ProcessState): El proceso del area de Running.
            y_start (int): La posición y inicial donde empezara el dibujo del cuadrado
            boxWidth (int): El tamaño del ancho del dibujo en pixeles
            boxHeight (int): El tamaño del alto del dibujo en pixeles
        """
        canvas.create_rectangle(
            350, yStart,
            350 + boxWidth, yStart + boxHeight,
            fill="lightgreen", tags="process"
        )
        canvas.create_text(
            350 + boxWidth // 2, yStart + boxHeight // 2,
            text=f"{"PID: "+str(runningArea.process.pid)}", tags="process"
        )

    def drawWaitingArea(self, canvas, waitingArea, x_start, yStart, boxWidth, boxHeight, gap):
        """
        Dibuja los procesos del area de waiting como cuadrados teniendo en cuenta waitingArea, para ello le asigna a los cuadrados un tamaño,
        un tag para identificarlos y una separación determinada(gap) respecto a los demas y los añade al canvas.
                
        Args:
            canvas (Canvas): El canvas correspondiente a actualizar.
            waitingArea (list): La lista del area de waiting.
            x_start (int): La posición x inicial donde empezara el dibujo del cuadrado
            y_start (int): La posición y inicial donde empezara el dibujo del cuadrado
            boxWidth (int): El tamaño del ancho del dibujo en pixeles
            boxHeight (int): El tamaño del alto del dibujo en pixeles
            gap (int): La separación del dibujo respecto a los demas cercanos
        """
        for i, process in enumerate(waitingArea):
            canvas.create_rectangle(
                x_start, yStart + i * (boxHeight + gap),
                x_start + boxWidth, yStart + i * (boxHeight + gap) + boxHeight,
                fill="lightblue", tags="process"
            )
            canvas.create_text(
                x_start + boxWidth // 2, yStart + i * (boxHeight + gap) + boxHeight // 2,
                text=f"{"PID: "+str(process.process.pid)}", tags="process"
            )

    def drawCompletedArea(self, canvas, completedArea, yStart, boxWidth, boxHeight, gap):
        """
        Dibuja los procesos del area de completed como cuadrados teniendo en cuenta waitingArea, para ello le asigna a los cuadrados un tamaño,
        un tag para identificarlos y una separación determinada(gap) respecto a los demas y los añade al canvas.
                
        Args:
            canvas (Canvas): El canvas correspondiente a actualizar.
            completedArea (list): La lista del area de completed.
            x_start (int): La posición x inicial donde empezara el dibujo del cuadrado
            y_start (int): La posición y inicial donde empezara el dibujo del cuadrado
            boxWidth (int): El tamaño del ancho del dibujo en pixeles
            boxHeight (int): El tamaño del alto del dibujo en pixeles
            gap (int): la separación del dibujo respecto a los demas cercanos
        """
        for i, process in enumerate(completedArea):
            canvas.create_rectangle(
                650, yStart + i * (boxHeight + gap),
                650 + boxWidth, yStart + i * (boxHeight + gap) + boxHeight,
                fill="lightgray", tags="process"
            )
            canvas.create_text(
                650 + boxWidth // 2, yStart + i * (boxHeight + gap) + boxHeight // 2,
                text=f"{"PID: "+str(process.process.pid)}", tags="process"
            )
    
    def showErrorMessage(self, message):
        """
        Muestra en pantalla mediante un popUp un aviso de error determinado
        
        Args:
            message (string): El mensaje de error dado
        """
        messagebox.showerror("Error", message)
    
    def cleanRows(self):
        """
        Limpia todas las filas de la tabla, para ello elimina todos los valores presentes en las casillas recorriendo la tabla fila por fila
        """
        for row in self.table.get_children():
            self.table.delete(row)
            
    def cleanInputs(self):
        """
        Limpia todos los campos de entrada y los deja vacios
        """
        self.arrivalTimeEntry.delete(0, tk.END) 
        self.pid_entry.delete(0, tk.END)
        self.burstTimeEntry.delete(0, tk.END)
    
    def addTableValues(self, processStates):
        """
        Añade los valores de la lista processStates en la tabla de la interfaz, para ello recorre todos los valores
        de la lista y los va añadiendo fila por fila en la tabla, estos valores los obtiene con el metodo getValues.
        Args:
            processStates (list): Lista de procesos.
        """
        for state in processStates:
            self.table.insert("", "end", values=state.getValues())
            
class TimeshareProcessingView(ISerieProcessingView):
    def __init__(self, parent, addProcess, runAnimation, updateTable):
        """
        Construye un objeto TimeshareProcessingView, este objeto permite gestionar la interfaz del programa de simulación,
        para ello define una estructura visual primero definiendo el tamaño y proporciones de la ventana principal, luego 
        inicializa una tabla que representara la simulación de una lista de procesos, esta tabla tendra las siguientes columnas:
        PID: el id del proceso
        AT: el tiempo de llegada del proceso
        BT: el tiempo que requiere el proceso para ejecutarse
        CT: el tiempo en el que el proceso terminó de ejecutarse
        TAT: el tiempo transcurrido del proceso desde su primera ejecución hasta cuando termino su ejecución.
        WT: el tiempo que estuvo el proceso en la cola de espera
        Las filas de la tabla representan los procesos, en estas filas se mostrara la información de los mismos.
        Ademas de la tabla se inicializan otros componentes, como botones para poder interactuar con la interfaz mediante
        eventos de click, por ende se añade un boton para el evento de añadir proceso, otro boton para el evento de ejecutar
        animación y otro para el evento de actualizar tabla y tambien campos de entrada(inputs) para recibir los datos necesarios como el PID, el ArrivalTime,
        el BurstTime y el Quantum y almacenarlos hasta cuando se requieran mediante eventos de teclado.
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
        
        tk.Label(self.inputFrame, text="Arrival Time:").pack(side=tk.LEFT, padx=5)
        self.arrivalTimeEntry = tk.Entry(self.inputFrame)
        self.arrivalTimeEntry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.inputFrame, text="Burst Time:").pack(side=tk.LEFT, padx=5)
        self.burstTimeEntry = tk.Entry(self.inputFrame)
        self.burstTimeEntry.pack(side=tk.LEFT, padx=5)
        
        self.quantumFrame = tk.Frame(self.frame)
        self.quantumFrame.pack(pady=10)

        tk.Label(self.quantumFrame, text="Duración del Quantum:").pack(side=tk.LEFT, padx=5)
        self.quantumEntry = tk.Entry(self.quantumFrame)
        self.quantumEntry.pack(side=tk.LEFT, padx=5)
        
        self.updateButton = tk.Button(self.quantumFrame, text="Actualizar tabla", command=updateTable)
        self.updateButton.pack(side=tk.LEFT, padx=5)
        
        self.buttonFrame = tk.Frame(self.frame)
        self.buttonFrame.pack(pady=10)

        self.addButton = tk.Button(self.buttonFrame, text="Añadir proceso", command=addProcess)
        self.addButton.pack(side=tk.LEFT, padx=5)

        self.animate_button = tk.Button(self.buttonFrame, text="Ejecutar animacion", command=runAnimation)
        self.animate_button.pack(side=tk.LEFT, padx=5)
        
    def drawAnimation(self, processStates, quantum):
        """
        Ejecuta una animación en una ventana secundaria, primero evaluando si hay por lo menos 1 proceso en processStates, de lo contrario manda un aviso de error y no permite
        mostrar la animación, esta animación representa el procesamiento segun el esquema en tiempo compartido por Round Robin para los procesos de 
        processStates dados, para ello utiliza un objeto canvas, este objeto permite renderizar y hacer graficos, es el que permite hacer la animación. Primero, inicializa 
        los valores predeterminados de la ventana como sus proporciones mediante el metodo createAnimationWindow. Luego de esto, compienza la animación, esta animación 
        maneja la logica de Round Robin representando cada proceso como un cuadrado con su PID dibujado en el centro, el conteo de la ejecución la maneja la variable currentTime, tambien
        esta variable se ira actualizando cada segundo por una unidad tambien mediante el metodo drawCurrent time se representa el tiempo actual graficamente segun currentTime y asignandole un tag, 
        el panel se divide en 3 columnas iguales la primera columna con el texto Waiting contendra en su interior los procesos(cuadrados) que se encuentran esperando por tiempo en la CPU,
        la segunda columna con el texto Running contendra el unico proceso que se ejecuta en un determinado momento y la tercera columna con el texto Completed
        contendra a aquellos procesos cuyo BurstTime(Tiempo de rafaga) ya se acabo, es decir fueron ejecutados por completo,
        a todos los cuadrados les asigna un tag, esto es para manipular los elementos con mayor facilidad, esto a nivel visual, a nivel
        logico hay una lista llamada waitingArea que almacena todos los procesos que actualmente se encuentran esperando, tambien un objeto RunningArea
        que sera el proceso que actualmente se encuentra ejecutandose y una lista llamada completedArea que almacena todos los procesos que fueron ejecutados
        completamente. En cada segundo de ejecución se dibujan los procesos de las 3 areas(waiting, running y completed), este dibujo se realiza
        dependiendo de los procesos que se encuentren en cada area, para dibujar y manejar la logica del proceso que se encuentra ejecutandose se usa el metodo
        processRunningProcess, para dibujar los procesos que esten en el area de waiting se usa el metodo drawWaitingArea y para dibujar
        los procesos que se encuentren en el area de Completed se usa el metodo drawCompletedArea.
        Entonces en la primera iteración de la animación se añaden todos los procesos en el area de waiting mediante el metodo addArrivingProcesses,
        luego se evalua si hay algun proceso en waitingArea o no hay en runningArea, en tal caso elimina el primer proceso en el area de waiting
        y lo asigna en el area de running, es decir pasa de estar en espera a ejecutarse. Posterior a esto ejecuta por 1 segundo el proceso, dibuja los 
        procesos en waiting y los de completed, aumenta el contador currentTime y hace que la animación dure 1 segundo hasta continuar su siguiente iteracion 
        mediante el metodo after del objeto canvas. En la siguiente iteración se limpia el canvas con el metodo clearCanvas, esto elimina los cuadrados de 
        procesos y el label de tiempo, lo que permite actualizarlos usando los tags de estos elementos, esto ocurre hasta que se ejecuta un quantum de un proceso en concreto,
        cada que se logra ejecutar este quantum en un proceso realiza un cambio de contexto y le reduce a este proceso su burstTime en un quantum, elimina el 
        proceso actual del area de running, lo añade como ultimo lugar en el area de waiting y asigna en el area de running al primer proceso del area de waiting, 
        realiza esto simultaneamente, una vez termina el burstTime de un proceso completamente añade el proceso en el area de completed mediante el metodo 
        processRunningProcess. Esto sucesivamente hasta que no halla ningun proceso ni en el area de waiting ni en la de running, esto significa que el 
        procesamiento termino, en este punto el currentTime se detiene.
        Args:
            processStates (list): Lista de procesos.
            quantum (int): Tiempo máximo que cada proceso puede ejecutarse antes de ser interrumpido y enviado al area de waiting.
        """
        if len(processStates) == 0:
            self.showErrorMessage("Debe añadir mínimo un proceso.")
            return

        animationWindow, canvas = self.createAnimationWindow()
        currentTime = 0
        x_start, yStart, boxWidth, boxHeight, gap = 50, 100, 100, 50, 10

        self.drawStaticLabels(canvas)

        waitingArea = []
        runningArea = None
        completedArea = []

        burstTime = None
        quantumCounter = quantum

        def update_canvas():
            nonlocal currentTime, waitingArea, runningArea, completedArea, burstTime, quantumCounter

            self.clearCanvas(canvas)
            self.drawCurrentTime(canvas, currentTime)

            self.addArrivingProcesses(processStates, waitingArea, currentTime)

            if not runningArea and waitingArea:
                runningArea = waitingArea.pop(0)

            runningArea, burstTime, quantumCounter = self.processRunningProcess(
                canvas, runningArea, waitingArea, completedArea, burstTime, quantumCounter, quantum, yStart, boxWidth, boxHeight
            )

            self.drawWaitingArea(canvas, waitingArea, x_start, yStart, boxWidth, boxHeight, gap)
            self.drawCompletedArea(canvas, completedArea, yStart, boxWidth, boxHeight, gap)

            currentTime += 1

            if runningArea or waitingArea or len(completedArea) < len(processStates):
                canvas.after(1000, update_canvas)

        update_canvas()


    def createAnimationWindow(self):
        """
        Inicializa los valores predeterminados de la ventana secundaria de la animación, asignandole los valores del tamaño de la ventana,
        nombre de la ventana, adicionalmente inicializa un canvas, este canvas permite hacer representaciones
        dinamicas de elementos visuales en la pantalla, le especifica sus proporciones, lo añade en la ventana principal de la animación
        y finalmente asigna el canvas a la ventana con el metodo pack.
        
        Returns:
            TopLevel: La ventana secundaria.
            Canvas: El contenedor canvas.
        """
        animationWindow = tk.Toplevel(self.frame)
        animationWindow.title("Animación de procesamiento por Round Robin")
        canvas = tk.Canvas(animationWindow, width=800, height=400, bg="white")
        canvas.pack()
        return animationWindow, canvas

    def drawStaticLabels(self, canvas):
        """
        Dibuja los 3 labels pertenecientes a cada area de procesos(waiting, running y completed) en el canvas
        
        Args:
            canvas (Canvas): El canvas correspondiente a actualizar.
        """
        canvas.create_text(100, 50, text="Waiting", font=("Arial", 14))
        canvas.create_text(400, 50, text="Running", font=("Arial", 14))
        canvas.create_text(700, 50, text="Completed", font=("Arial", 14))

    def clearCanvas(self, canvas):
        """
        Limpia los dibujos del canvas pertenecientes al tag process(los procesos) y al tag time(el tiempo actual)
        
        Args:
            canvas (Canvas): El canvas correspondiente a actualizar.
        """
        canvas.delete("process")
        canvas.delete("time")

    def drawCurrentTime(self, canvas, currentTime):
        """
        Dibuja el valor de currentTime en el canvas
                
        Args:
            canvas (Canvas): El canvas correspondiente a actualizar.
            currentTime (int): El tiempo actual.
        """
        canvas.create_text(400, 20, text=f"Tiempo actual: {currentTime}", font=("Arial", 16), tag="time")

    def addArrivingProcesses(self, processStates, waitingArea, currentTime):
        """
        Añade los procesos en la lista de llegada processStates en el area de waiting cuyo arrivalTime es igual al currentTime(llegaron a la cola de espera), 
        para ello recorre todos los procesos de processStates y evalua si el arrivalTime de cada proceso es igual al currentTime,
        si ese es el caso añade el proceso al area de waiting, de lo contrario no.
                
        Args:
            processStates (list): Lista de procesos.
            waitingArea (list): La lista del area de waiting.
            currentTime (int): El tiempo actual.
        """
        for process in processStates:
            if process.arrivalTime == currentTime:
                waitingArea.append(process)

    def processRunningProcess(self, canvas, runningArea, waitingArea, completedArea, burstTime, quantumCounter, quantum, yStart, boxWidth, boxHeight):
        """
        Gestiona la ejecución del proceso en el area de running, para ello primero evalua si el area de running es diferente de None,
        si es asi entonces significa que hay un proceso ejecutandose, luego evalua si el burstTime es None, el burstTime es None en
        la primera ejecución de algun programa, tambien evalua si es -1, este es -1 cuando hubo un cambio de contexto o el ultimo proceso en el
        area de running fue ejecutado por completo, en este caso le asigna al burstTime el burstTime del proceso en el area de running.
        Posteriormente evalua si el quantumCounter(contador del quantum) es igual a 0, esto ocurre cuando el proceso actual completa un quantum de ejecución
        seguido, tambien evalua si el burstTime actual es mayor a 0, esto es para evitar errores cuando hubo cambio de contexto reciente y 
        que se haga otro inmediatamente, en el caso que estas 2 condiciones se cumplan se ejecuta un cambio de contexto, en este caso lo que ocurre
        es que el proceso en el area de running se mueve al area de waiting como ultimo y el primero del area de waiting se añade al area running, 
        tambien el quantumCounter se reinicia al valor de quantum - 1, el burstTime actual se asigna como -1 y se reduce el burstTime del proceso actual
        en 1 segundo para continuar la ejecución del siguiente proceso en el area de waiting.
        Posteriormente evalua si el burstTime del proceso actual es igual a 1, si es asi añade el proceso al area de completed y
        lo elimina del runningArea, luego asigna en el area de running al primer proceso del area de waiting pero
        unicamente si la longitud de waitingArea es mayor a 0, es decir aun hay procesos en espera, ademas evalua si el burstTime actual es 0
        si estas 2 condiciones se cumplen asigna el proceso como None, cuando esto ocurre significa que la animación debe terminar porque no hay procesos 
        ni en waiting ni en running y reduce en 1 segundo el burstTime actual para sincronizarlo con el currentTime. 
        Luego luego reduce en un segundo el burstTime actual, el quantumCounter y el burstTime del proceso actual.
        Finalmente dibuja el proceso del area de running como cuadrado teniendo en cuenta runningArea, para ello le asigna a los 
        cuadrados un tamaño, un tag para identificarlos y los añade al canvas.
                
        Args:
            canvas (Canvas): El canvas correspondiente a actualizar.
            runningArea (ProcessState): El proceso del area de Running.
            waitingArea (list): La lista del area de waiting.
            completedArea (list): La lista del area de completed.
            burstTime (int): El tiempo de rafaga actual.
            quantumCounter (int): Contador del tiempo máximo restante que el proceso del area de running puede ejecutarse antes de ser interrumpido y enviado al area de waiting.
            quantum (int): Tiempo máximo que cada proceso puede ejecutarse antes de ser interrumpido y enviado al area de waiting.
            y_start (int): La posición y inicial donde empezara el dibujo del cuadrado
            boxWidth (int): El tamaño del ancho del dibujo en pixeles
            boxHeight (int): El tamaño del alto del dibujo en pixeles
        
        Returns:
            runningArea (ProcessState): El proceso que se encuentra en el area de running.
            burstTime (int): El tiempo de rafaga actual.
            quantumCounter (int): Contador del tiempo máximo restante que el proceso del area de running puede ejecutarse antes de ser interrumpido y enviado al area de waiting.
        """
        if runningArea:
            if burstTime is None or burstTime == -1:
                burstTime = runningArea.process.burstTime

            if quantumCounter == 0 and burstTime > 0:
                waitingArea.append(copy.deepcopy(runningArea))
                if runningArea.process.pid == waitingArea[0].process.pid:
                    waitingArea.pop(0)
                if len(waitingArea) > 1:
                    runningArea = waitingArea.pop(0)
                elif len(waitingArea) == 0 and runningArea.process.burstTime == 0:
                    runningArea = None

                quantumCounter = quantum - 1
                burstTime = -1
                if runningArea is not None:
                    runningArea.process.burstTime -= 1

            if burstTime == 0:
                completedArea.append(copy.deepcopy(runningArea))
                if len(waitingArea) > 0:
                    runningArea = waitingArea.pop(0)
                if len(waitingArea) == 0 and runningArea.process.burstTime == 0:
                    runningArea = None
                burstTime = -1
                quantumCounter = quantum - 1
                if runningArea is not None:
                    runningArea.process.burstTime -= 1

            if burstTime is not None and burstTime > 0:
                burstTime -= 1
                quantumCounter -= 1
                runningArea.process.burstTime -= 1

            if runningArea is not None:
                canvas.create_rectangle(
                    350, yStart,
                    350 + boxWidth, yStart + boxHeight,
                    fill="lightgreen", tags="process"
                )
                canvas.create_text(
                    350 + boxWidth // 2, yStart + boxHeight // 2,
                    text=f"{"PID: "+str(runningArea.process.pid)}", tags="process"
                )

        return runningArea, burstTime, quantumCounter

    def drawWaitingArea(self, canvas, waitingArea, x_start, yStart, boxWidth, boxHeight, gap):
        """
        Dibuja los procesos del area de waiting como cuadrados teniendo en cuenta waitingArea, para ello le asigna a los cuadrados un tamaño,
        un tag para identificarlos y una separación determinada(gap) respecto a los demas y los añade al canvas.
                
        Args:
            canvas (Canvas): El canvas correspondiente a actualizar.
            waitingArea (list): La lista del area de waiting.
            x_start (int): La posición x inicial donde empezara el dibujo del cuadrado
            y_start (int): La posición y inicial donde empezara el dibujo del cuadrado
            boxWidth (int): El tamaño del ancho del dibujo en pixeles
            boxHeight (int): El tamaño del alto del dibujo en pixeles
            gap (int): La separación del dibujo respecto a los demas cercanos
        """
        for i, process in enumerate(waitingArea):
            canvas.create_rectangle(
                x_start, yStart + i * (boxHeight + gap),
                x_start + boxWidth, yStart + i * (boxHeight + gap) + boxHeight,
                fill="lightblue", tags="process"
            )
            canvas.create_text(
                x_start + boxWidth // 2, yStart + i * (boxHeight + gap) + boxHeight // 2,
                text=f"{"PID: "+str(process.process.pid)}", tags="process"
            )

    def drawCompletedArea(self, canvas, completedArea, yStart, boxWidth, boxHeight, gap):
        """
        Dibuja los procesos del area de completed como cuadrados teniendo en cuenta waitingArea, para ello le asigna a los cuadrados un tamaño,
        un tag para identificarlos y una separación determinada(gap) respecto a los demas y los añade al canvas.
                
        Args:
            canvas (Canvas): El canvas correspondiente a actualizar.
            completedArea (list): La lista del area de completed.
            x_start (int): La posición x inicial donde empezara el dibujo del cuadrado
            y_start (int): La posición y inicial donde empezara el dibujo del cuadrado
            boxWidth (int): El tamaño del ancho del dibujo en pixeles
            boxHeight (int): El tamaño del alto del dibujo en pixeles
            gap (int): la separación del dibujo respecto a los demas cercanos
        """
        for i, process in enumerate(completedArea):
            canvas.create_rectangle(
                650, yStart + i * (boxHeight + gap),
                650 + boxWidth, yStart + i * (boxHeight + gap) + boxHeight,
                fill="lightgray", tags="process"
            )
            canvas.create_text(
                650 + boxWidth // 2, yStart + i * (boxHeight + gap) + boxHeight // 2,
                text=f"{"PID: "+str(process.process.pid)}", tags="process"
            )
    
    def showErrorMessage(self, message):
        """
        Muestra en pantalla mediante un popUp un aviso de error determinado
        
        Args:
            message (string): El mensaje de error dado
        """
        messagebox.showerror("Error", message)
    
    def cleanRows(self):
        """
        Limpia todas las filas de la tabla, para ello elimina todos los valores presentes en las casillas recorriendo la tabla fila por fila
        """
        for row in self.table.get_children():
            self.table.delete(row)
            
    def cleanInputs(self):
        """
        Limpia todos los campos de entrada y los deja vacios
        """
        self.arrivalTimeEntry.delete(0, tk.END) 
        self.pid_entry.delete(0, tk.END)
        self.burstTimeEntry.delete(0, tk.END)
    
    
    def addTableValues(self, processStates):
        """
        Añade los valores de la lista processStates en la tabla de la interfaz, para ello recorre todos los valores
        de la lista y los va añadiendo fila por fila en la tabla, estos valores los obtiene con el metodo getValues.
        Args:
            processStates (list): Lista de procesos.
        """
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
        self.arrivalTimeEntry = tk.Entry(self.inputFrame)
        self.arrivalTimeEntry.pack(side=tk.LEFT, padx=5)
        
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
                if process.arrivalTime == currentTime:
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
        self.arrivalTimeEntry.delete(0, tk.END) 
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
        self.timeshareProcessingTab = None
        self.batchProcessingTab = None
        self.batchMultiProcessingTab = None

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
        
    def configureTimeshareProcessingTab(self, timeshareController):
        """
        Configura la pestaña de procesamiento en serie.

        Args:
            serieController (SerieProcessingController): Controlador para el procesamiento en serie.

        Returns:
            None
        """
        self.timeshareProcessingTab = TimeshareProcessingView(
            self.notebook, timeshareController.addProcess, timeshareController.runAnimation, timeshareController.updateTable
        )
        self.notebook.add(self.timeshareProcessingTab.frame, text="Procesamiento en Tiempo compartido")

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
        self.notebook.add(self.batchProcessingTab.frame, text="Procesamiento por Lotes/Monoprogramación")

    def configureBatchMultiProcessingTab(self):
        """
        Configura la pestaña de procesamiento por lotes.

        Args:
            batchController (BatchProcessingController): Controlador para el procesamiento por lotes.

        Returns:
            None
        """
        self.batchMultiProcessingTab = BatchMultiProcessingView(
            self.notebook
        )
        self.notebook.add(self.batchMultiProcessingTab.frame, text="Procesamiento por Lotes/Multiprogramación")

    def run(self):
        """
        Inicia el bucle principal de la aplicación.

        Args:
            None

        Returns:
            None
        """
        self.root.mainloop()



