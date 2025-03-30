import concurrent.futures
import itertools
import multiprocessing
import time
import Pyro4
from subject import start_server
from observer import main

def send_request(server_uri):
    try:
        with Pyro4.Proxy(server_uri) as proxy:
            return proxy.insult_me()
    except Exception as e:
        return f"Error contacting {server_uri}: {e}"

class RoundRobin:
    def __init__(self, num_servers):
        self.SERVERS = []
        self.processes = []
        self.processes_observers = []

        for i in range(num_servers):
            pyro_uri = f"PYRONAME:example.observable{i}"
            self.SERVERS.append(pyro_uri)

            p = multiprocessing.Process(target=start_server, args=(f"example.observable{i}",))
            p.start()
            self.processes.append(p)
            time.sleep(1)

        self.server_cycle = itertools.cycle(self.SERVERS)

    def get_next_server(self):
        return next(self.server_cycle)

    def insult_me(self):
        server_uri = self.get_next_server()
        print(f"Forwarding request to: {server_uri}")
        try:
            with Pyro4.Proxy(server_uri) as proxy:
                return proxy.insult_me()
        except Exception as e:
            print(f"Failed to contact {server_uri}: {e}")
            return "Error: Server unavailable"

    def get_insults(self, num_requests):
        server_uris = [self.get_next_server() for _ in range(num_requests)]

        start_time = time.perf_counter_ns()

        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(send_request, uri) for uri in server_uris]

        end_time = time.perf_counter_ns()

        elapsed_time = (end_time - start_time) / 1e9
        print(f"Time used to complete {num_requests} requests: {elapsed_time} seconds")

        return futures

    def close_servers(self):
        for p in self.processes_observers:
            p.terminate()
        for p in self.processes_observers:
            p.join()

        for p in self.processes:
            p.terminate()
        for p in self.processes:
            p.join()

    def add_subs(self, num_subs, num_servers):
        for i in range(num_subs):
            p = multiprocessing.Process(target=main, args=(num_servers,))
            p.start()
            self.processes.append(p)
            time.sleep(1)


if __name__ == "__main__":
    num_servers = 1

    round_robin = RoundRobin(num_servers)

    try:
        result = round_robin.get_insults(100)
        finish = time.perf_counter_ns()
        #print(result)

    finally:
        round_robin.close_servers()
