import pika
import multiprocessing
import time
from InsultServer import start_server


class LoadBalancer:
    def __init__(self, num_servers, queue_name='insultQueue'):
        self.num_servers = num_servers
        self.queue_name = queue_name
        self.processes = []

    def start_servers(self, event):
        for _ in range(self.num_servers):
            process = multiprocessing.Process(target=start_server, args=(self.queue_name, event))
            process.start()
            self.processes.append(process)

    def stop_servers(self):
        for process in self.processes:
            process.terminate()
            process.join()



def callback(ch, method, properties, body, message_count, stop_event, start_time):
    message = body.decode()
    print(f"Insult received: {message}")

    if message_count[0] >= 100:
        elapsed_time_ns = time.perf_counter_ns() - start_time
        elapsed_time_s = elapsed_time_ns / 1e9
        print(f"Received {message_count[0]} insults, elapsed time: {elapsed_time_s:.4f} seconds.")
        stop_event.set()
        print("Received 100 insults, stopping consumption.")
        ch.stop_consuming()

    message_count[0] += 1

def run_load_balancer():
    message_count = [0]
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_purge(queue='insultQueue')
    stop_event = multiprocessing.Event()

    channel.queue_declare(queue='insultQueue')

    load_balancer = LoadBalancer(num_servers=3, queue_name='insultQueue')
    load_balancer.start_servers(stop_event)

    try:
        start = time.perf_counter_ns()

        channel.basic_consume(
            queue='insultQueue',
            on_message_callback=lambda ch, method, properties, body: callback(ch, method, properties, body, message_count, stop_event, start),
            auto_ack=True
        )

        channel.start_consuming()

    except KeyboardInterrupt:
        print("Stopping processes...")
        load_balancer.stop_servers()
        connection.close()

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    run_load_balancer()

