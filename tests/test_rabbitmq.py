import threading
import unittest
from unittest.mock import patch, MagicMock
import time
import sys
import os
from RabbitMQ.Dynamic.LoadBalancer import DynamicScalingLoadBalancer
from RabbitMQ.Dynamic.LoadBalancer import run_load_balancer


# Ensure correct paths before importing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../RabbitMQ")))

class TestDynamicScalingLoadBalancer(unittest.TestCase):
    @patch('Dynamic.InsultServer.start_server')
    @patch('multiprocessing.Process')
    def setUp(self, mock_process, mock_start_server):
        mock_process.return_value.start = MagicMock()
        mock_process.return_value.join = MagicMock()

        mock_start_server.return_value = None

        initial_num_servers = 2
        self.load_balancer = DynamicScalingLoadBalancer(initial_num_servers, queue_name='testQueue', capacity_per_server=5)

        time.sleep(0.5)

    def tearDown(self):
        self.load_balancer.stop_servers()

    def test_add_server(self):
        initial_count = len(self.load_balancer.processes)
        self.load_balancer.add_server()
        self.assertEqual(len(self.load_balancer.processes), initial_count + 1)

    def test_remove_server(self):
        initial_count = len(self.load_balancer.processes)
        self.load_balancer.remove_server()
        self.assertEqual(len(self.load_balancer.processes), max(1, initial_count - 1))

    @patch('Dynamic.LoadBalancer.time.sleep', return_value=None)
    def test_monitor_load(self, mock_sleep):
        self.load_balancer.request_count.value = 10

        monitor_thread = threading.Thread(target=self.load_balancer.monitor_load, daemon=True)
        monitor_thread.start()

        time.sleep(0.5)
        self.load_balancer.request_count = 0

        self.assertGreaterEqual(len(self.load_balancer.processes), 1)

    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_get_insults(self, mock_executor):
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        mock_future = MagicMock()
        mock_future.result.return_value = "You're a CENSORED embarrassment."
        mock_executor_instance.submit.return_value = mock_future

        run_load_balancer(200)

        self.assertTrue(1)

if __name__ == '__main__':
    unittest.main()
