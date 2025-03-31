# Instrucciones para ejecutar los tests en Scaling-Distributed-Systems

## Requisitos previos
Para ejecutar los tests contenidos en la carpeta `tests` de este repositorio, asegúrate de cumplir con los siguientes requisitos:

### 1. Descargar el repositorio
Clona este repositorio en tu máquina local:
```sh
 git clone https://github.com/mimigald/Scaling-Distributed-Systems.git
 cd Scaling-Distributed-Systems
```

### 2. Tener Python 3.8+
Asegúrate de tener instalado Python en la versión 3.8 o superior.

### 3. Instalar Pyro4 y ejecutar el Pyro Name Server
Pyro4 es necesario para la comunicación remota entre procesos. Instálalo con:
```sh
pip install Pyro4
```
Luego, inicia el Pyro Name Server en el puerto designado para permitir el registro y búsqueda de objetos remotos:
```sh
python -m Pyro4.naming
```

### 4. Instalar Docker
Si aún no tienes Docker instalado, sigue estos pasos según tu sistema operativo:

**Para Linux:**
```sh
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

**Para macOS:**
- Descarga e instala Docker desde [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Inicia la aplicación Docker Desktop

**Para Windows:**
- Descarga e instala Docker desde [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Activa la virtualización en la BIOS si es necesario

### 5. Descargar Redis en Docker
Ejecuta los siguientes comandos para descargar y ejecutar Redis en un contenedor Docker:
```sh
docker pull redis
```
Para ejecutar Redis en un contenedor:
```sh
docker run --name redis -d -p 6379:6379 redis
```

### 6. Configurar RabbitMQ en Docker
Ejecuta los siguientes comandos para configurar y correr RabbitMQ:
```sh
docker pull rabbitmq:management
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```
Accede al panel de control de RabbitMQ desde:
[http://localhost:15672](http://localhost:15672)

Credenciales de acceso por defecto:
- Usuario: `guest`
- Contraseña: `guest`

Instala la librería Pika para interactuar con RabbitMQ en Python:
```sh
pip3 install pika==1.3.1
```
Implementa y prueba los ejemplos de `Hello World` y `Work Queue` utilizando distintas formas de serialización:
- Pickle
- String encode/bytes decode
- JSON encode/decode

### 7. Ejecutar el state-remote-installer
Dentro del repositorio, ejecuta el script de instalación para configurar `tcl` en un sistema virtual:
```sh
./state-remote-installer.sh
```

### 8. Ejecutar los tests desde PyCharm
Después de completar todas las configuraciones anteriores, puedes ejecutar los tests directamente desde PyCharm, seleccionando la carpeta `tests` y ejecutándolos con el intérprete de Python configurado correctamente.

---
