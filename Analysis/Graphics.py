import matplotlib.pyplot as plt

# To run this file use the next command in terminal
# Open a terminal in this file
# state shell Python-3.11.11-Windows
# python .\Graphics.py

# How many requests can do per second
systems = ['XMLRPC', 'PyRO', 'Redis', 'RabbitMQ']
requests_per_second = [3.8771, 0.9727, 9.7993, 437.0293]  # These values are placeholders

# Plot
plt.figure(figsize=(10, 6))
plt.bar(systems, requests_per_second, color=['blue', 'green', 'red', 'purple'])
plt.title('Single-node Performance Analysis')
plt.xlabel('Communication Systems')
plt.ylabel('Requests per Second')
plt.show()

# The number of requests will be 100 for each system
nodes = [1, 2, 3]
xmlrpc_times = [18.4626, 18.4369, 18.4659]  # Time taken for 1, 2, and 3 nodes
pyro_times = [64.8736, 64.8287, 64.8147]
redis_times = [10.2048, 5.2015, 3.6283]
rabbitmq_times = [0.2288, 0.2687, 0.2880]

# Plotting multiple lines for each system
plt.figure(figsize=(10, 6))
plt.plot(nodes, xmlrpc_times, label='XMLRPC', marker='o')
plt.plot(nodes, pyro_times, label='PyRO', marker='o')
plt.plot(nodes, redis_times, label='Redis', marker='o')
plt.plot(nodes, rabbitmq_times, label='RabbitMQ', marker='o')

plt.title('Multiple-node Static Scaling Performance')
plt.xlabel('Number of Nodes')
plt.ylabel('Time (Seconds)')
plt.legend()
plt.show()


xmlrpc_speedup = [xmlrpc_times[0] / time for time in xmlrpc_times]
pyro_speedup = [pyro_times[0] / time for time in pyro_times]
redis_speedup = [redis_times[0] / time for time in redis_times]
rabbitmq_speedup = [rabbitmq_times[0] / time for time in rabbitmq_times]

# Plotting speedup for each system
plt.figure(figsize=(10, 6))
plt.plot(nodes, xmlrpc_speedup, label='XMLRPC Speedup', marker='o')
plt.plot(nodes, pyro_speedup, label='PyRO Speedup', marker='o')
plt.plot(nodes, redis_speedup, label='Redis Speedup', marker='o')
plt.plot(nodes, rabbitmq_speedup, label='RabbitMQ Speedup', marker='o')

plt.title('Speedup in Multiple-node Static Scaling')
plt.xlabel('Number of Nodes')
plt.ylabel('Speedup')
plt.legend()
plt.show()


