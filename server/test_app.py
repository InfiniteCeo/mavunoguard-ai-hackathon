import unittest
from fastapi.testclient import TestClient
from server.app import app

class TestAppEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_manifest(self):
        response = self.client.get("/static/manifest.webmanifest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "MavunoGuard AI")

    def test_icons(self):
        for icon in ["icon-192.png", "icon-512.png", "icon-maskable-512.png"]:
            response = self.client.get(f"/static/icons/{icon}")
            self.assertEqual(response.status_code, 200)

    def test_service_worker(self):
        response = self.client.get("/sw.js")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
