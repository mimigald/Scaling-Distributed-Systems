import concurrent.futures
import xmlrpc.client
import itertools
import multiprocessing
import time
import threading
from InsultServer import start_server

class DynamicScalingRoundRobin:
    def __init__(self, initial_servers, capacity_per_worker):
        self.server_cycle = None
        self.SERVERS = []
        self.processes = []
        self.lock = threading.Lock()
        self.capacity_per_worker = capacity_per_worker
        self.request_count = 0
        self.start_time = time.time()
        self.monitor_interval = 5  # Intervalo de monitoreo en segundos

        # Iniciar servidores iniciales
        for _ in range(initial_servers):
            self.add_server()

        # Iniciar hilo de monitoreo
        self.monitor_thread = threading.Thread(target=self.monitor_load, daemon=True)
        self.monitor_thread.start()

    def add_server(self):
        """Añade un servidor dinámicamente."""
        server_id = len(self.SERVERS)
        port = 8000 + server_id
        url = f"http://localhost:{port}"
        self.SERVERS.append(url)

        # Iniciar el servidor en un nuevo proceso
        p = multiprocessing.Process(target=start_server, args=(port,))
        p.start()
        self.processes.append(p)
        time.sleep(1)

        # Actualizar el ciclo de balanceo
        self.server_cycle = itertools.cycle(self.SERVERS)

    def remove_server(self):
        """Elimina un servidor si hay más de uno disponible."""
        if len(self.SERVERS) > 1:
            server_url = self.SERVERS.pop()
            process = self.processes.pop()
            process.terminate()
            process.join()
            print(f"Servidor {server_url} eliminado.")

            # Actualizar el ciclo de balanceo
            self.server_cycle = itertools.cycle(self.SERVERS)

    def get_next_server(self):
        """Obtiene la URL del próximo servidor."""
        return next(self.server_cycle)

    def send_request(self, server_url):
        """Envía una solicitud al siguiente server de la cola Round Robin."""
        try:
            proxy = xmlrpc.client.ServerProxy(server_url)
            return proxy.get_insult()
        except Exception as e:
            return f"Error contactando {server_url}: {e}"

    def insult_me(self):
        self.request_count += 1  # Contabilizar solicitudes
        server_url = self.get_next_server()
        print(f"Forwarding request to: {server_url}")

        try:
            proxy = xmlrpc.client.ServerProxy(server_url)
            return proxy.insult_me()
        except Exception as e:
            print(f"Fallo al contactar {server_url}: {e}")
            return "Error: Servidor no disponible"

    def get_insults(self, num_requests):
        """Procesar solicitudes en paralelo."""
        start_time = time.perf_counter_ns()
        futures = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for _ in range(num_requests):
                with self.lock:
                    self.request_count += 1
                    server_uri = self.get_next_server()
                futures.append(executor.submit(self.send_request, server_uri))
        end_time = time.perf_counter_ns()

        elapsed_time = (end_time - start_time) / 1e9
        print(f"Tiempo para completar {num_requests} solicitudes: {elapsed_time} segundos")
        return futures

    def monitor_load(self):
        """Monitorea la carga y ajusta el número de servidores dinámicamente."""
        while True:
            time.sleep(self.monitor_interval)

            # Calcular tasa de llegada de mensajes λ
            elapsed_time = time.time() - self.start_time
            with self.lock:
                arrival_rate = self.request_count/elapsed_time if elapsed_time > 0 else 0

            # Calcular servidores que fan falta
            avg_processing_time = 0.26
            required_servers = max(1, round((arrival_rate * avg_processing_time) / self.capacity_per_worker))

            print(f"Tasa de llegada: {arrival_rate:.2f} msg/s | Servidores requeridos: {required_servers}")

            # Aumentar o disminuir servidores según la necesidad
            with self.lock:
                current_servers = len(self.SERVERS)

                if required_servers > current_servers:
                    for _ in range(required_servers - current_servers):
                        self.add_server()
                elif required_servers < current_servers:
                    for _ in range(current_servers - required_servers):
                        self.remove_server()

                # Resetear contadores
                self.request_count = 0
                self.start_time = time.time()

    def close_servers(self):
        """Cierra todos los servidores en ejecución."""
        with self.lock:
            for p in self.processes:
                p.terminate()
            for p in self.processes:
                p.join()
            self.SERVERS.clear()
            self.processes.clear()

if __name__ == "__main__":
    initial_servers = 2
    capacity_per_worker = 3

    round_robin = DynamicScalingRoundRobin(initial_servers, capacity_per_worker)

    try:
        result = round_robin.get_insults(200)
    finally:
        round_robin.close_servers()
