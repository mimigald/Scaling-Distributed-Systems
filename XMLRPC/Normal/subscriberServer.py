from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import sys
import multiprocessing

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class SubscriberServer:
    def notify(self, insult):
        """Receive notification of a new insult."""
        print(f"Received insult: {insult}")
        return "Insult received."

def start_subscriber(PORT):
    with SimpleXMLRPCServer(('localhost', PORT), requestHandler=RequestHandler, allow_none=True) as server:
        server.register_instance(SubscriberServer())
        print(f"Subscriber Server running on port {PORT}...")
        server.serve_forever()

if __name__ == "__main__":
    try:
        num_subscribers = 3
    except (IndexError, ValueError):
        print("Usage: python subscriber.py <num_subscribers>")
        sys.exit(1)

    base_port = 8020  # Start from port 8020
    processes = []

    for i in range(num_subscribers):
        port = base_port + i
        process = multiprocessing.Process(target=start_subscriber, args=(port,))
        process.start()
        processes.append(process)

    try:
        for process in processes:
            process.join()  # Keeps the processes running
    except KeyboardInterrupt:
        print("\nShutting down subscriber servers.")
        for process in processes:
            process.terminate()
        sys.exit(0)
