import multiprocessing
import time
from concurrent.futures import ThreadPoolExecutor

import redis
from Redis.Dynamic.InsultServer import start_server
import threading


class DynamicScalingLoadBalancer:
    def __init__(self, initial_num_processes, queue_name, capacity_per_server):
        self.queue_name = queue_name
        self.capacity_per_server = capacity_per_server
        self.processes = []
        self.num_processes = initial_num_processes

        # Variables que se comparten entre procesos
        self.manager = multiprocessing.Manager()
        self.request_count = self.manager.Value('i', 0)
        self.lock = self.manager.Lock()
        self.stop_event = multiprocessing.Event()

        # Iniciar los procesos y el monitoreo
        self.start_processes()
        self.monitor_thread = threading.Thread(target=self.monitor_load)
        self.monitor_thread.start()

    def start_processes(self):
        """Inicia múltiples procesos de servidor."""
        for _ in range(self.num_processes):
            self.add_server()

    def stop_processes(self):
        """Detiene todos los procesos en ejecución."""
        self.stop_event.set()
        for process in self.processes:
            process.terminate()
            process.join()
        self.processes.clear()

    def insult_me(self):
        """Obtiene un insulto de la cola."""
        client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        text = client.rpop(self.queue_name)
        while text is None:
            text = client.rpop(self.queue_name)
        return text

    def add_server(self):
        """Agrega un nuevo servidor."""
        process = multiprocessing.Process(target=start_server, args=(self.queue_name, self.stop_event))
        process.start()
        self.processes.append(process)
        print("Servidor agregado.")

    def remove_server(self):
        """Elimina un servidor."""
        if self.processes:
            process = self.processes.pop()
            process.terminate()
            process.join()
            print("Servidor eliminado.")

    def process_request(self):
        """Procesa una solicitud y la cuenta."""
        with self.lock:
            self.request_count.value += 1
        return self.insult_me()

    def monitor_load(self):
        """Monitorea la carga y ajusta la cantidad de servidores dinámicamente."""
        start_time = time.time()
        while not self.stop_event.is_set():
            time.sleep(3)

            with self.lock:
                elapsed_time = time.time() - start_time
                arrival_rate = self.request_count.value / elapsed_time if elapsed_time > 0 else 0
                avg_processing_time = 0.1
                required_servers = max(1, round((arrival_rate * avg_processing_time) / self.capacity_per_server))

                print(f"Tasa de llegada: {arrival_rate:.2f} msg/s | Servidores requeridos: {required_servers}")

                # Ajustar servidores según la tasa de llegada
                if required_servers > len(self.processes):
                    for _ in range(required_servers - len(self.processes)):
                        self.add_server()
                elif required_servers < len(self.processes):
                    for _ in range(len(self.processes) - required_servers):
                        self.remove_server()

                # Reset de contadores
                self.request_count.value = 0
                start_time = time.time()


if __name__ == "__main__":
    initial_num_processes = 1
    queue_name = "insult_queue"
    capacity_per_server = 10

    lb = DynamicScalingLoadBalancer(initial_num_processes, queue_name, capacity_per_server)

    try:
        finish = 0
        start = time.perf_counter_ns()
        # Uso ThreadPoolExecutor para lanzar las solicitudes concurrentes (no sé si es correcto :/)
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(lb.process_request) for i in range(1000)]

            for i, future in enumerate(futures):
                insult = future.result()  # Obtener el resultado del insulto
                print(f"Insulto {i} recibido: {insult}")
                if i == 999:
                    finish = time.perf_counter_ns()
                    lb.stop_event.set()
        elapsed_time_ns = finish - start
        elapsed_time_s = elapsed_time_ns / 1e9
        print(f"Tiempo utilizado: {elapsed_time_s} s")
    except KeyboardInterrupt:
        print("Deteniendo los procesos...")
    finally:
        lb.stop_processes()
        lb.monitor_thread.join()
