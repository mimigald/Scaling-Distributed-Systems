from time import sleep
import Pyro4

# Crea el proxy para interactuar con el servicio de filtro de insultos
insultFilter = Pyro4.Proxy("PYRONAME:example.observable")

# Lista de insultos
insultList = ["fuck you", "asshole", "you're a bitch!"]

def start_insult():
    for insult in insultList:
        # Envía el insulto al filtro
        insultFilter.filter_message(insult)
        print(f"Insult sent: {insult}")
        sleep(5)  # Espera 5 segundos antes de enviar el siguiente insulto

if __name__ == "__main__":
    start_insult()