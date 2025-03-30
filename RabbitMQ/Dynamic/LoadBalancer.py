import pika
import multiprocessing
import threading
import time
from RabbitMQ.Dynamic.InsultServer import start_server


class DynamicScalingLoadBalancer:
    def __init__(self, initial_num_servers, queue_name='insultQueue', capacity_per_server=5):
        self.queue_name = queue_name
        self.capacity_per_server = capacity_per_server
        self.processes = []
        self.num_processes = initial_num_servers

        # El manager se encarga de las variables compartidas entre procesos
        self.manager = multiprocessing.Manager()
        self.request_count = self.manager.Value('i', 0)  # Valor compartido para el conteo
        self.lock = self.manager.Lock()  # Para sincronizar procesos
        self.start_time = time.time()

        # Lanzar servidores iniciales
        self.start_servers()

        # Lanzar proceso de monitoreo
        self.monitor_thread = threading.Thread(target=self.monitor_load)
        self.monitor_thread.start()

    def start_servers(self):
        self.stop_event = multiprocessing.Event()
        for _ in range(self.num_processes):
            process = multiprocessing.Process(target=start_server, args=(self.queue_name, self.stop_event))
            process.start()
            self.processes.append(process)

    def stop_servers(self):
        for process in self.processes:
            process.terminate()
            process.join()

    def add_server(self):
        process = multiprocessing.Process(target=start_server, args=(self.queue_name, self.stop_event))
        process.start()
        self.processes.append(process)
        print("Server added.")

    def remove_server(self):
        if self.processes:
            process = self.processes.pop()
            process.terminate()
            process.join()
            print("Server removed.")

    def monitor_load(self):
        while True:
            time.sleep(5)

            # Calcula el arrival rate λ (requests per second)
            elapsed_time = time.time() - self.start_time
            arrival_rate = self.request_count.value / elapsed_time if elapsed_time > 0 else 0

            # Calcula el número de servidores con la formula N = λ * T / C
            avg_processing_time = 1.0
            required_servers = max(1, round((arrival_rate * avg_processing_time) / self.capacity_per_server))

            print(f"Arrival rate: {arrival_rate:.2f} msg/s | Required servers: {required_servers}")

            with self.lock:
                current_servers = len(self.processes)

                if required_servers > current_servers:
                    for _ in range(required_servers - current_servers):
                        self.add_server()
                elif required_servers < current_servers:
                    for _ in range(current_servers - required_servers):
                        self.remove_server()

                self.request_count.value = 0
                self.start_time = time.time()


def callback(ch, method, properties, body, message_count, stop_event, start_time, num_rq):
    message = body.decode()
    print(f"Insult received: {message}")

    if message_count[0] >= num_rq:
        elapsed_time_ns = time.perf_counter_ns() - start_time
        elapsed_time_s = elapsed_time_ns / 1e9
        print(f"Received {message_count[0]} insults, elapsed time: {elapsed_time_s:.4f} seconds.")
        stop_event.set()
        print(f"Received {num_rq} insults, stopping consumption.")
        ch.stop_consuming()

    message_count[0] += 1


def run_load_balancer(num_req):
    message_count = [0]
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='insultQueue')

    channel.queue_purge(queue='insultQueue')

    stop_event = multiprocessing.Event()

    load_balancer = DynamicScalingLoadBalancer(initial_num_servers=3, queue_name='insultQueue', capacity_per_server=5)

    try:
        start = time.perf_counter_ns()

        channel.basic_consume(
            queue='insultQueue',
            on_message_callback=lambda ch, method, properties, body: callback(ch, method, properties, body, message_count, stop_event, start, num_req),
            auto_ack=True
        )

        channel.start_consuming()

    except KeyboardInterrupt:
        print("Stopping processes...")
        load_balancer.stop_servers()
        connection.close()


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    run_load_balancer(200)
