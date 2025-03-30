import Pyro4
import multiprocessing

@Pyro4.expose
class Observer:
    def update(self, message):
        """This method is called when the observable sends a notification."""
        print(f"🔔 Received update: {message}")

def main(num_servers):
    observables = []
    ns = Pyro4.locateNS()
    for i in range (num_servers):
        observable = Pyro4.Proxy(ns.lookup(f"example.observable{i}"))
        observables.append(observable)

    with Pyro4.Daemon() as daemon:
        observer = Observer()
        observer_uri = daemon.register(observer)  # Get remote URI

        for server in observables:
            server.register_observer(observer_uri)  # Register observer with the observable
        
        print(f"Observer registered with URI: {observer_uri}")
        print("🔄 Waiting for notifications...")

        daemon.requestLoop()  # Keep the observer running to receive updates

if __name__ == "__main__":
    main()
