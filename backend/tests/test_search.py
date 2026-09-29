"""
===============================================================================
NWIS Backend - Semantic Search Integration Tests (Phase 3)
===============================================================================
Validates:
1. Normal text and PDF document search
2. Semantic search for known hazard categories:
   - Mud Loss in Demo-Barail
   - Stuck Pipe in Demo-Kopili Shale
   - Gas Kick in Demo-Tipam Sandstone
   - Cementing issue across intermediate casing
3. Formation name search
4. Depth-related queries
===============================================================================
"""

import sys
import os
import unittest

# Ensure backend and project root are in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from app.main import app


class TestSemanticSearchAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_search_mud_loss(self):
        """Verify semantic search retrieves Barail mud loss reports."""
        response = self.client.get("/api/search?query=severe mud loss in Demo-Barail sandstone")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertGreater(len(data["results"]), 0)
        # Verify result contains relevance score
        top_result = data["results"][0]
        self.assertIn("score", top_result)
        self.assertGreater(top_result["score"], 0.0)

    def test_02_search_stuck_pipe(self):
        """Verify semantic search retrieves Kopili stuck pipe incidents."""
        response = self.client.get("/api/search?query=stuck pipe and jarring overpull in Kopili shale")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data["results"]), 0)

    def test_03_search_gas_kick(self):
        """Verify semantic search retrieves Tipam gas kick well control reports."""
        response = self.client.get("/api/search?query=gas kick pit gain drilling break in Tipam")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data["results"]), 0)

    def test_04_search_cementing_issue(self):
        """Verify semantic search retrieves casing cementing channeling reports."""
        response = self.client.get("/api/search?query=casing cementing issue channeling CBL squeeze")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data["results"]), 0)

    def test_05_search_formation_name(self):
        """Verify search specifically targeting formation names returns results."""
        response = self.client.get("/api/search?query=Demo-Girujan Clay interval")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data["results"]), 0)

    def test_06_search_depth_related(self):
        """Verify search using depth-related language."""
        response = self.client.get("/api/search?query=incident around 3520m depth")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data["results"]), 0)

    def test_07_search_validation_error(self):
        """Verify single character query fails validation (min_length=2)."""
        response = self.client.get("/api/search?query=a")
        self.assertEqual(response.status_code, 422)

    def test_08_search_top_k_parameter(self):
        """Verify top_k parameter caps the number of results."""
        response = self.client.get("/api/search?query=drilling operations&top_k=2")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertLessEqual(len(data["results"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
