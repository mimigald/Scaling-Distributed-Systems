import xmlrpc.client
import time
from LoadBalancer import RoundRobin

# Envía insultos al filtro cada 5 segundos
insults = ["Fuck you.", "Asshole.", "You're a bitch."]
load_balancer = RoundRobin(1)

if __name__ == "__main__":
    time.sleep(4)
    for insult in insults:
        result = load_balancer.send_insult(insult)
        print(f"Result: {result}")
        time.sleep(5)