import threading
import unittest
import time
import multiprocessing
from unittest.mock import patch, MagicMock
from Pyro.Dynamic.LoadBalancer import DynamicScalingRoundRobin

# Ensure correct paths before importing
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Pyro')))


if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("spawn")
    except RuntimeError:
        pass

class TestLoadBalancer(unittest.TestCase):

    @patch("Dynamic.subject.start_server")
    @patch("Pyro4.Proxy")
    def setUp(self, mock_pyro_proxy, mock_start_server):
        mock_pyro_proxy.return_value = MagicMock()
        mock_pyro_proxy.return_value.insult_me.return_value = "You're a CENSORED embarrassment."
        self.load_balancer = DynamicScalingRoundRobin(initial_servers=2, capacity_per_worker=1)
        time.sleep(0.5)

    def test_monitor_load(self):
        monitor_thread = threading.Thread(target=self.load_balancer.monitor_load, daemon=True)
        monitor_thread.start()

        time.sleep(0.5)
        self.load_balancer.request_count = 0

        self.assertGreaterEqual(len(self.load_balancer.SERVERS), 1)

    def test_insult_detection(self):
        insult = self.load_balancer.insult_me()
        self.assertIn("CENSORED", insult)

if __name__ == "__main__":
    unittest.main()
