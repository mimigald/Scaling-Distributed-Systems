import threading
import unittest
from unittest.mock import patch, MagicMock
import time
import sys
import os

# Ensure correct paths before importing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../XMLRPC/Dynamic")))

from XMLRPC.Dynamic.LoadBalancer import DynamicScalingRoundRobin

class TestDynamicScalingRoundRobin(unittest.TestCase):
    @patch('XMLRPC.Dynamic.InsultServer.start_server')
    @patch('xmlrpc.client.ServerProxy')  # Correct patching
    def setUp(self, mock_server_proxy, mock_start_server):
        self.mock_proxy_instance = MagicMock()
        mock_server_proxy.return_value = self.mock_proxy_instance
        self.mock_proxy_instance.insult_me.return_value = "You're a CENSORED embarrassment."

        self.load_balancer = DynamicScalingRoundRobin(initial_servers=2, capacity_per_worker=3)
        time.sleep(0.5)

    def tearDown(self):
        self.load_balancer.close_servers()

    def test_add_server(self):
        initial_count = len(self.load_balancer.SERVERS)
        self.load_balancer.add_server()
        self.assertEqual(len(self.load_balancer.SERVERS), initial_count + 1)

    def test_remove_server(self):
        initial_count = len(self.load_balancer.SERVERS)
        self.load_balancer.remove_server()
        self.assertEqual(len(self.load_balancer.SERVERS), max(1, initial_count - 1))

    def test_get_next_server(self):
        server1 = self.load_balancer.get_next_server()
        server2 = self.load_balancer.get_next_server()
        self.assertNotEqual(server1, server2)

    def test_send_request(self):
        server_url = "http://localhost:8000"
        response = self.load_balancer.send_request(server_url)
        self.assertTrue(response)

    def test_insult_me(self):
        insult = self.load_balancer.insult_me()
        self.assertTrue(insult)

    @patch('XMLRPC.Dynamic.LoadBalancer.time.sleep', return_value=None)
    def test_monitor_load(self, mock_sleep):
        self.load_balancer.request_count = 10

        monitor_thread = threading.Thread(target=self.load_balancer.monitor_load, daemon=True)
        monitor_thread.start()

        time.sleep(0.5)
        self.load_balancer.request_count = 0

        self.assertGreaterEqual(len(self.load_balancer.SERVERS), 1)

    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_get_insults(self, mock_executor):
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        mock_future = MagicMock()
        mock_future.result.return_value = "You're a CENSORED embarrassment."
        mock_executor_instance.submit.return_value = mock_future

        futures = self.load_balancer.get_insults(100)
        results = [future.result() for future in futures]

        for insult in results:
            self.assertTrue(insult)

if __name__ == '__main__':
    unittest.main()
