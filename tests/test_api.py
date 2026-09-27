import json
import os
import sys
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.index import app


class TestActiveDirectoryReaperAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")

    def test_graph_endpoint(self):
        res = self.client.get("/api/graph")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertGreater(len(data["nodes"]), 0)

    def test_metrics_endpoint(self):
        res = self.client.get("/api/metrics")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("episodes", data)
        self.assertIn("rewards", data)
        self.assertEqual(len(data["episodes"]), len(data["rewards"]))

    def test_train_endpoint(self):
        res = self.client.post("/api/train")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("status", data)
        self.assertIn("output", data)

    def test_benchmark_endpoint(self):
        res = self.client.post("/api/benchmark")
        self.assertEqual(res.status_code, 200)
        text = res.get_data(as_text=True)
        self.assertIn("BENCHMARK RESULTS", text)

    def test_frontend_static_serving(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn("Active Directory Reaper", html)


if __name__ == "__main__":
    unittest.main()
