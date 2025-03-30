import threading
import unittest
import time
import multiprocessing
from unittest.mock import patch, MagicMock
from Redis.Dynamic.LoadBalancer import DynamicScalingLoadBalancer
from Redis.Dynamic.InsultServer import start_server

# Ensure correct paths before importing
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Redis')))

if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("spawn")
    except RuntimeError:
        pass

class TestLoadBalancer(unittest.TestCase):

    @patch("Dynamic.InsultServer.start_server")
    @patch("redis.Redis")
    def setUp(self, mock_redis, mock_start_server):
        mock_redis.return_value = MagicMock()
        mock_redis.return_value.get.return_value = "Simulated message from Redis."

        self.load_balancer = DynamicScalingLoadBalancer(initial_num_processes=2, queue_name='testQueue', capacity_per_server=5)
        time.sleep(0.5)

    def test_monitor_load(self):
        monitor_thread = threading.Thread(target=self.load_balancer.monitor_load, daemon=True)
        monitor_thread.start()

        time.sleep(0.5)
        self.load_balancer.request_count = 0

        self.assertGreaterEqual(len(self.load_balancer.processes), 1)

    def test_insult_detection(self):
        insult = self.load_balancer.insult_me()
        self.assertIn("CENSORED", insult)

if __name__ == "__main__":
    unittest.main()
