import time
import multiprocessing
from InsultServer import start_server
import redis


class LoadBalancer:
    def __init__(self, num_proc, queue_name):
        self.num_processes = num_proc
        self.queue_name = queue_name
        self.processes = []

    def start_processes(self, event):
        for _ in range(self.num_processes):
            process = multiprocessing.Process(target=start_server, args=(self.queue_name, event))
            process.start()
            self.processes.append(process)

    def stop_processes(self):
        for process in self.processes:
            process.terminate()
            process.join()

    def insult_me(self):
        client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        text = client.rpop(self.queue_name)
        while text is None:
            text = client.rpop(self.queue_name)
        return text

if __name__ == "__main__":
    num_processes = 1
    lb = LoadBalancer(num_processes, "insult_queue")
    stop_event = multiprocessing.Event()

    lb.start_processes(stop_event)

    try:
        start = time.perf_counter_ns()
        finish = 0
        for i in range(100):
            insult = lb.insult_me()
            print(f"Insult {i} received: {insult}")
            if i == 99:
                finish = time.perf_counter_ns()
                stop_event.set()
        lb.stop_processes()
        elapsed_time_ns = finish - start
        elapsed_time_s = elapsed_time_ns / 1e9
        print(f"Time used: {elapsed_time_s} s")
    except KeyboardInterrupt:
        print("Stopping processes...")
        lb.stop_processes()
