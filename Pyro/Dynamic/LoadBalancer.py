import concurrent.futures
import itertools
import multiprocessing
import time
import Pyro4
import threading
import Pyro4.errors
from Pyro.Dynamic.subject import start_server



class DynamicScalingRoundRobin:
    def __init__(self, initial_servers, capacity_per_worker):
        self.server_cycle = None
        self.SERVERS = []
        self.processes = []
        self.lock = threading.Lock()
        self.capacity_per_worker = capacity_per_worker
        self.request_count = 0
        self.start_time = time.time()
        self.monitor_interval = 5  # Monitoreo cada 5 segundos

        # Iniciar servidores iniciales
        for i in range(initial_servers):
            self.add_server()

        # Lanzar thread de monitoreo de carga
        self.monitor_thread = threading.Thread(target=self.monitor_load, daemon=True)
        self.monitor_thread.start()

    def add_server(self):
        server_id = len(self.SERVERS)
        pyro_uri = f"PYRONAME:example.observable{server_id}"

        # Iniciar el servidor en un nuevo proceso
        p = multiprocessing.Process(target=start_server, args=(f"example.observable{server_id}",))
        p.start()
        self.processes.append(p)

        time.sleep(0.25)  # Espera antes de intentar conectarse

        for _ in range(5):  # Intentar conexión hasta 5 veces
            try:
                with Pyro4.Proxy(pyro_uri) as proxy:
                    proxy._pyroBind()
                break
            except Pyro4.errors.CommunicationError:
                print(f"Esperando que el servidor {server_id} esté listo...")
                time.sleep(1)

        # Añadir al ciclo solo si está activo
        self.SERVERS.append(pyro_uri)
        self.server_cycle = itertools.cycle(self.SERVERS[:])

    def remove_server(self):
        with self.lock:
            if len(self.SERVERS) > 1 and self.processes:
                server_uri = self.SERVERS.pop()
                process = self.processes.pop()
                process.terminate()
                process.join()
                print(f"Servidor {server_uri} eliminado.")

                self.server_cycle = itertools.cycle(self.SERVERS[:])

    def get_next_server(self):
        with self.lock:
            if not self.server_cycle:
                self.server_cycle = itertools.cycle(self.SERVERS[:])
            return next(self.server_cycle)

    def insult_me(self):
        self.request_count += 1  # Contabilizar solicitudes
        server_uri = self.get_next_server()
        try:
            with Pyro4.Proxy(server_uri) as proxy:
                return proxy.insult_me()
        except Exception as e:
            print(f"Fallo al contactar {server_uri}: {e}")
            return "Error: Servidor no disponible"

    def get_insults(self, num_requests):
        start_time = time.perf_counter_ns()
        futures = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for _ in range(num_requests):
                self.request_count += 1
                server_uri = self.get_next_server()
                futures.append(executor.submit(self.send_request, server_uri))
                time.sleep(0.05)  # Para evitar sobrecarga

        end_time = time.perf_counter_ns()
        elapsed_time = (end_time - start_time) / 1e9
        print(f"Tiempo para completar {num_requests} solicitudes: {elapsed_time} segundos")
        return futures

    @staticmethod
    def send_request(server_uri):
        """Ejecuta una petición en un proceso (thread) separado."""
        try:
            with Pyro4.Proxy(server_uri) as proxy:
                return proxy.insult_me()
        except Exception as e:
            return f"Error contactando {server_uri}: {e}"

    def monitor_load(self):
        """Monitorea la carga del sistema y ajusta la cantidad de servidores en función de la demanda."""
        while True:
            time.sleep(self.monitor_interval)
            with self.lock:
                elapsed_time = time.time() - self.start_time
                arrival_rate = self.request_count / elapsed_time if elapsed_time > 0 else 0

                avg_processing_time = 1.0
                required_servers = max(1, round((arrival_rate * avg_processing_time) / self.capacity_per_worker))

                print(f"Tasa de llegada: {arrival_rate:.2f} pts/s | Servidores requeridos: {required_servers}")

                current_servers = len(self.SERVERS)
                if required_servers > current_servers:
                    for _ in range(required_servers - current_servers):
                        self.add_server()
                elif required_servers < current_servers:
                    if elapsed_time > 10:  # Esperar al menos 10s antes de eliminar servidores
                        for _ in range(current_servers - required_servers):
                            self.remove_server()

                self.request_count = 0
                self.start_time = time.time()

    def close_servers(self):
        """Cierra todos los servidores activos."""
        with self.lock:
            for p in self.processes:
                p.terminate()
            for p in self.processes:
                p.join()
            self.SERVERS.clear()
            self.processes.clear()
            self.server_cycle = None  # Reiniciar ciclo


if __name__ == "__main__":
    initial_servers = 2
    capacity_per_worker = 1

    round_robin = DynamicScalingRoundRobin(initial_servers, capacity_per_worker)

    try:
        result = round_robin.get_insults(200)
    finally:
        round_robin.close_servers()
