# RoundRobin.py
import concurrent.futures
import xmlrpc.client
import itertools
import multiprocessing
import time
from InsultServer import start_server


class RoundRobin:
    def __init__(self, num_servers):
        # List of available servers (adding more if needed)
        self.SERVERS = []
        self.processes = []
        for i in range(num_servers):
            port = 8000 + i
            url = f"http://localhost:{port}"
            self.SERVERS.append(url)
            # Start each server in a separate process
            p = multiprocessing.Process(target=start_server, args=(port,))
            p.start()
            self.processes.append(p)
            time.sleep(1)
        # Create a round-robin iterator
        self.server_cycle = itertools.cycle(self.SERVERS)

    def get_next_server(self):
        """Returns the next server in round-robin order."""
        return next(self.server_cycle)

    def send_insult(self, message):
        """Sends an insult to the next server in round-robin order."""
        server_url = self.get_next_server()
        print(f"Forwarding request to: {server_url}")

        try:
            proxy = xmlrpc.client.ServerProxy(server_url)
            return proxy.filter_insult(message)
        except Exception as e:
            print(f"Failed to contact {server_url}: {e}")
            return "Error: Server unavailable"

    def insult_me(self):
        server_url = self.get_next_server()
        print(f"Forwarding request to: {server_url}")

        try:
            proxy = xmlrpc.client.ServerProxy(server_url)
            return proxy.insult_me()
        except Exception as e:
            print(f"Failed to contact {server_url}: {e}")
            return "Error: Server unavailable"

    def send_request(self, server_url):
        try:
            proxy = xmlrpc.client.ServerProxy(server_url)
            return proxy.get_insult()
        except Exception as e:
            return f"Error contacting {server_url}: {e}"

    def get_insult(self, num_requests):
        # Start measuring time
        start_time = time.perf_counter_ns()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.send_request, self.get_next_server()) for _ in range(num_requests)]
        # End measuring time
        end_time = time.perf_counter_ns()

        # Calculate elapsed time in seconds
        elapsed_time = (end_time - start_time) / 1e9
        print(f"Time used to complete {num_requests} requests: {elapsed_time} seconds")

        return futures

    def close_servers(self):
        """Terminate all server processes."""
        for p in self.processes:
            p.terminate()
        for p in self.processes:
            p.join()

    def add_subs(self, url, num_server):
        for i in range (num_server):
            server_url = self.get_next_server()  # InsultServer
            proxy = xmlrpc.client.ServerProxy(server_url)
            proxy.add_subscriber(url)


if __name__ == "__main__":
    num_servers = 3
    subscribers_url = ["http://localhost:8020", "http://localhost:8021", "http://localhost:8022"]
    # Create RoundRobin instance
    round_robin = RoundRobin(num_servers)

    # Sample insults to send
    #insults = ["Fuck you.", "Asshole.", "You're a bitch."]
    #time.sleep(3)
    #for subs in subscribers_url:
    #    round_robin.add_subs(subs, num_servers)
    try:

        result = round_robin.get_insult(100)
        # print (result)
    finally:
        round_robin.close_servers()  # Ensure servers are properly closed after use
