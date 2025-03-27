import tkinter as tk
from tkinter import ttk
from tkinter import ttk, messagebox
from IClassesModels import ISerieProcessingView

class SerieProcessingView(ISerieProcessingView):
    def __init__(self, addProcess, runAnimation):
        
        self.root = tk.Tk()
        self.root.title("Tabla de procesos(Procesamiento en serie)")
        
        windowWidth = 800
        windowHeight = 400
        screenWidth = self.root.winfo_screenwidth()
        screenHeight = self.root.winfo_screenheight()
        positionX = (screenWidth // 2) - (windowWidth // 2)
        positionY = (screenHeight // 2) - (windowHeight // 2)
        self.root.geometry(f"{windowWidth}x{windowHeight}+{positionX}+{positionY}")
        
        self.columns = ("PID", "AT", "BT", "CT", "TAT", "WT")
        self.table = ttk.Treeview(self.root, columns=self.columns, show="headings", height=10)
        
        for col in self.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100)
        
        self.table.pack(pady=10)
        
        self.inputFrame = tk.Frame(self.root)
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
        
        self.buttonFrame = tk.Frame(self.root)
        self.buttonFrame.pack(pady=10)

        self.addButton = tk.Button(self.buttonFrame, text="Añadir proceso", command=addProcess)
        self.addButton.pack(side=tk.LEFT, padx=5)

        self.animate_button = tk.Button(self.buttonFrame, text="Ejecutar animacion", command=runAnimation)
        self.animate_button.pack(side=tk.LEFT, padx=5)
        
    def drawAnimation(self, processStates):
        if len(processStates) == 0:
            self.showErrorMessage("Debe añadir minimo un proceso.")
            return
        
        animationWindow = tk.Toplevel(self.root)
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