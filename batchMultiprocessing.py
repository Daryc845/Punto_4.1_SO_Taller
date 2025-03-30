import tkinter as tk
import random
import time
from threading import Thread, Lock, Event
from queue import Queue
from tkinter import ttk, messagebox

# Modelo
class Process:
    def __init__(self, id, tiempo_ejecucion, lote_id=None):
        """
        Representa un proceso en el sistema de multiprogramación por lotes.
        
        Args:
            id (int): Identificador único del proceso.
            tiempo_ejecucion (int): Tiempo total requerido para la ejecución del proceso.
            lote_id (int, optional): Identificador del lote al que pertenece el proceso. Defaults to None.
        """
        self.id = id
        self.tiempo_ejecucion = tiempo_ejecucion
        self.tiempo_restante = tiempo_ejecucion  # Tiempo restante de ejecución
        self.lote_id = lote_id  # Lote al que pertenece el proceso

class Lote:
    def __init__(self, lote_id, processs=None):
        """
        Representa un lote de procesos para ejecución en multiprogramación.
        
        Args:
            lote_id (int): Identificador único del lote.
            processs (list, optional): Lista inicial de procesos. Defaults to None.
        """
        self.id = lote_id
        self.processs = processs if processs else []  # Lista de procesos en el lote
    
    def agregar_process(self, process):
        """
        Añade un proceso al lote y establece su lote_id.
        
        Args:
            process (Process): Proceso a agregar al lote.
        """
        process.lote_id = self.id
        self.processs.append(process)
    
    def esta_completo(self):
        """
        Verifica si todos los procesos del lote han completado su ejecución.
        
        Returns:
            bool: True si todos los procesos tienen tiempo_restante = 0, False en caso contrario.
        """
        return len(self.processs) > 0 and all(p.tiempo_restante == 0 for p in self.processs)

# Controlador
class ControllerSimulation:
    def __init__(self, vista):
        """
        Controlador que gestiona la simulación de multiprogramación por lotes.
        
        Args:
            vista (BatchMultiProcessingView): Vista asociada al controlador.
        """
        self.vista = vista
        self.lotes = []  # Lista de lotes de procesos
        self.processs_en_ejecucion = []  # Procesos actualmente en ejecución
        self.quantum = tk.IntVar(value=2)  # Tiempo quantum para cada proceso
        self.num_processs = tk.IntVar(value=5)  # Número total de procesos
        self.num_procesadores = tk.IntVar(value=4)  # Número de procesadores disponibles
        self.num_lotes = tk.IntVar(value=2)  # Número de lotes
        self.lock = Lock()  # Lock para sincronización de hilos
        self.stop_event = Event()  # Evento para detener la simulación
        self.simulacion_activa = False  # Estado de la simulación
        self.simulacion_thread = None  # Hilo de ejecución de la simulación
        self.modo_ejecucion = tk.StringVar(value="lotes_paralelo")  # Modo de ejecución: "lotes_paralelo" o "processs_paralelo"
    
    def generar_processs(self):
        """
        Genera lotes con procesos aleatorios, distribuyéndolos equitativamente entre los lotes.
        Los tiempos de ejecución se generan aleatoriamente entre 4 y 12 unidades de tiempo.
        """
        self.lotes = []
        processs_por_lote = self.num_processs.get() // self.num_lotes.get()
        
        for lote_id in range(self.num_lotes.get()):
            lote = Lote(lote_id + 1)
            
            for i in range(processs_por_lote):
                process_id = lote_id * processs_por_lote + i + 1
                tiempo_ejecucion = random.randint(4, 12)
                process = Process(process_id, tiempo_ejecucion, lote_id + 1)
                lote.agregar_process(process)
            
            self.lotes.append(lote)

    def ejecutar_processs_lotes_paralelo(self):
        """
        Ejecuta los lotes en paralelo, asignando cada lote a uno o más procesadores disponibles.
        Cada procesador ejecuta los procesos de su lote asignado usando round-robin con el quantum especificado.
        """
        def ejecutar_lote(procesador_id, lote):
            """
            Función interna que ejecuta los procesos de un lote en un procesador específico.
            
            Args:
                procesador_id (int): Identificador del procesador asignado.
                lote (Lote): Lote de procesos a ejecutar.
            """
            for process in lote.processs:
                while process.tiempo_restante > 0:
                    if self.stop_event.is_set():
                        return
                    
                    # Registrar proceso en ejecución
                    with self.lock:
                        self.processs_en_ejecucion.append((procesador_id, process))
                    
                    # Ejecutar por el quantum o tiempo restante
                    tiempo_a_ejecutar = min(self.quantum.get(), process.tiempo_restante)
                    process.tiempo_restante -= tiempo_a_ejecutar
                    
                    # Actualizar vista con animación
                    self.vista.animar_process(procesador_id, process.id, lote.id, tiempo_a_ejecutar)
                    
                    # Simular tiempo de ejecución con verificación periódica de parada
                    start_time = time.time()
                    while time.time() - start_time < tiempo_a_ejecutar:
                        if self.stop_event.is_set():
                            return
                        time.sleep(0.1)
                    
                    # Eliminar proceso de la lista de ejecución
                    with self.lock:
                        if (procesador_id, process) in self.processs_en_ejecucion:
                            self.processs_en_ejecucion.remove((procesador_id, process))
        
        # Distribuir lotes entre procesadores disponibles
        threads = []
        num_procesadores = self.num_procesadores.get()
        
        # Asignar lotes a procesadores (round-robin simple)
        for i, lote in enumerate(self.lotes):
            procesador_id = i % num_procesadores
            thread = Thread(target=ejecutar_lote, args=(procesador_id, lote))
            threads.append(thread)
            thread.start()
        
        # Esperar a que todos los hilos terminen
        for thread in threads:
            thread.join()
        
        # Actualizar vista final si no se detuvo la simulación
        if not self.stop_event.is_set():
            self.processs_en_ejecucion = []
            self.vista.actualizar_vista()
        
        # Restablecer estado de la simulación
        self.simulacion_activa = False
        self.vista.actualizar_botones()

    def ejecutar_processs_paralelo(self):
        """
        Ejecuta los procesos en paralelo dentro de cada lote, distribuyendo los procesos
        de cada lote entre los procesadores disponibles usando round-robin con quantum.
        """
        def ejecutar_procesador(procesador_id, process):
            """
            Función interna que ejecuta un proceso en un procesador específico.
            
            Args:
                procesador_id (int): Identificador del procesador.
                process (Process): Proceso a ejecutar.
            """
            while process.tiempo_restante > 0:
                if self.stop_event.is_set():
                    return
                
                # Registrar proceso en ejecución
                with self.lock:
                    self.processs_en_ejecucion.append((procesador_id, process))
                
                # Ejecutar por el quantum o tiempo restante
                tiempo_a_ejecutar = min(self.quantum.get(), process.tiempo_restante)
                process.tiempo_restante -= tiempo_a_ejecutar
                
                # Actualizar vista con animación
                self.vista.animar_process(procesador_id, process.id, process.lote_id, tiempo_a_ejecutar)
                
                # Simular tiempo de ejecución con verificación periódica de parada
                start_time = time.time()
                while time.time() - start_time < tiempo_a_ejecutar:
                    if self.stop_event.is_set():
                        return
                    time.sleep(0.1)
                
                # Eliminar proceso de la lista de ejecución
                with self.lock:
                    if (procesador_id, process) in self.processs_en_ejecucion:
                        self.processs_en_ejecucion.remove((procesador_id, process))
        
        # Ejecutar lotes secuencialmente, pero procesos en paralelo dentro de cada lote
        for lote in self.lotes:
            if self.stop_event.is_set():
                break
                
            threads = []
            # Distribuir procesos del lote entre los procesadores disponibles
            for i, process in enumerate(lote.processs):
                if process.tiempo_restante > 0:
                    procesador_id = i % self.num_procesadores.get()
                    thread = Thread(target=ejecutar_procesador, args=(procesador_id, process))
                    threads.append(thread)
                    thread.start()
            
            # Esperar a que terminen todos los procesos del lote actual
            for thread in threads:
                thread.join()
                
            self.vista.actualizar_vista()
            
        # Restablecer estado de la simulación
        self.simulacion_activa = False
        self.vista.actualizar_botones()
    
    def iniciar_simulacion(self):
        """
        Inicia la simulación generando los procesos y ejecutándolos según el modo seleccionado.
        """
        # Restablecer estado de la simulación
        self.stop_event.clear()
        self.simulacion_activa = True
        self.vista.actualizar_botones()
        
        # Generar procesos y actualizar vista inicial
        self.generar_processs()
        self.vista.actualizar_vista()
        
        # Ejecutar en modo seleccionado
        if self.modo_ejecucion.get() == "lotes_paralelo":
            self.simulacion_thread = Thread(target=self.ejecutar_processs_lotes_paralelo)
        else:
            self.simulacion_thread = Thread(target=self.ejecutar_processs_paralelo)
        
        self.simulacion_thread.start()
    
    def detener_simulacion(self):
        """
        Detiene la simulación en curso y limpia el estado.
        """
        if self.simulacion_activa:
            self.stop_event.set()
            self.simulacion_activa = False
            self.vista.actualizar_botones()
            # Limpiar lista de procesos en ejecución
            self.processs_en_ejecucion = []
            self.vista.actualizar_vista()

# Vista
class BatchMultiProcessingView:
    def __init__(self, parent):
        """
        Vista que gestiona la interfaz gráfica para la simulación de multiprogramación por lotes.
        
        Args:
            parent (tk.Widget): Widget padre donde se colocará esta vista.
        """
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True)
        
        self.controlador = ControllerSimulation(self)
        
        # Frame para configuración
        self.frame_config = tk.Frame(self.frame)
        self.frame_config.pack()
        
        # Controles de entrada
        tk.Label(self.frame_config, text="Número de Processs:").grid(row=0, column=0, sticky="w")
        tk.Entry(self.frame_config, textvariable=self.controlador.num_processs, width=5).grid(row=0, column=1)
        
        tk.Label(self.frame_config, text="Quantum:").grid(row=1, column=0, sticky="w")
        tk.Entry(self.frame_config, textvariable=self.controlador.quantum, width=5).grid(row=1, column=1)
        
        tk.Label(self.frame_config, text="Número de Procesadores:").grid(row=2, column=0, sticky="w")
        tk.Entry(self.frame_config, textvariable=self.controlador.num_procesadores, width=5).grid(row=2, column=1)
        
        tk.Label(self.frame_config, text="Número de Lotes:").grid(row=3, column=0, sticky="w")
        tk.Entry(self.frame_config, textvariable=self.controlador.num_lotes, width=5).grid(row=3, column=1)
        
        # Opciones de modo de ejecución
        self.frame_modo = tk.Frame(self.frame)
        self.frame_modo.pack(pady=5)
        
        tk.Label(self.frame_modo, text="Modo de ejecución:").pack(side=tk.LEFT)
        
        tk.Radiobutton(self.frame_modo, text="Lotes en paralelo", variable=self.controlador.modo_ejecucion, 
                    value="lotes_paralelo").pack(side=tk.LEFT)
        
        tk.Radiobutton(self.frame_modo, text="Processs en paralelo", variable=self.controlador.modo_ejecucion, 
                    value="processs_paralelo").pack(side=tk.LEFT)
        
        # Canvas para visualización
        self.canvas = tk.Canvas(self.frame, width=700, height=400)
        self.canvas.pack()
        
        # Frame para botones
        self.frame_botones = tk.Frame(self.frame)
        self.frame_botones.pack(pady=10)
        
        self.btn_iniciar = tk.Button(self.frame_botones, text="Iniciar Simulación", 
                                    command=self.controlador.iniciar_simulacion)
        self.btn_iniciar.pack(side=tk.LEFT, padx=10)
        
        self.btn_detener = tk.Button(self.frame_botones, text="Detener Simulación", 
                                    command=self.controlador.detener_simulacion, 
                                    state=tk.DISABLED)
        self.btn_detener.pack(side=tk.LEFT, padx=10)
    
    def actualizar_botones(self):
        """
        Actualiza el estado de los botones según el estado actual de la simulación.
        """
        if self.controlador.simulacion_activa:
            self.btn_iniciar.config(state=tk.DISABLED)
            self.btn_detener.config(state=tk.NORMAL)
        else:
            self.btn_iniciar.config(state=tk.NORMAL)
            self.btn_detener.config(state=tk.DISABLED)
    
    def animar_process(self, procesador_id, process_id, lote_id, tiempo):
        """
        Anima la ejecución de un proceso en un procesador específico.
        
        Args:
            procesador_id (int): Identificador del procesador.
            process_id (int): Identificador del proceso.
            lote_id (int): Identificador del lote.
            tiempo (int): Tiempo de ejecución a animar.
        """
        x_start = 50
        y_start = 50 + (procesador_id * 60)
        
        # Limpiar área del procesador
        self.canvas.create_rectangle(x_start-10, y_start-30, 650, y_start+40, fill="white")
        
        # Mostrar información del proceso en ejecución
        self.canvas.create_text(x_start + 250, y_start - 15, 
                            text=f"P{process_id} en CPU {procesador_id} (Lote {lote_id})", 
                            font=("Arial", 12, "bold"))
        
        # Animar barra de progreso
        for i in range(1, 11):
            if self.controlador.stop_event.is_set():
                break
                
            ancho = i * 40
            self.canvas.create_rectangle(x_start, y_start, x_start + ancho, y_start + 30, 
                                        fill="#1ABC9C")
            self.frame.update()
            time.sleep(tiempo / 10)
        
        if not self.controlador.stop_event.is_set():
            self.actualizar_vista()
    
    def actualizar_vista(self):
        """
        Actualiza la interfaz gráfica mostrando el estado actual de los lotes y procesos.
        """
        self.canvas.delete("all")
        
        # Mostrar título
        self.canvas.create_text(350, 20, text="Cola de Processs por Lote", 
                            font=("Arial", 14, "bold"), fill="#ECF0F1")
        
        # Mostrar lotes y sus procesos
        y_offset = 50
        x_offset = 50
        
        for lote in self.controlador.lotes:
            # Mostrar información del lote
            self.canvas.create_text(x_offset, y_offset, 
                                text=f"Lote {lote.id}:", 
                                font=("Arial", 12, "bold"), fill="#ECF0F1", anchor="w")
            y_offset += 25
            
            # Mostrar procesos del lote
            for process in lote.processs:
                color = "#27AE60" if process.tiempo_restante == 0 else "#E74C3C"
                
                self.canvas.create_text(x_offset + 20, y_offset, 
                                    text=f"P{process.id} - {process.tiempo_restante}s restantes", 
                                    font=("Arial", 10), fill=color, anchor="w")
                y_offset += 20
            
            y_offset += 20
        
        # Mostrar procesos en ejecución
        y_offset = 200
        self.canvas.create_text(350, y_offset, 
                            text="Processs en Ejecución", 
                            font=("Arial", 14, "bold"), fill="#ECF0F1")
        y_offset += 30
        
        for cpu_id, process in self.controlador.processs_en_ejecucion:
            self.canvas.create_text(350, y_offset, 
                            text=f"CPU {cpu_id}: Ejecutando P{process.id} (Lote {process.lote_id}) - {process.tiempo_restante}s restantes", 
                            font=("Arial", 10), fill="#123458")
            y_offset += 20