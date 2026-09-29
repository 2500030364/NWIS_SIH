"""
===============================================================================
NWIS Backend - API Integration Tests
===============================================================================
Tests all core REST endpoints against the existing Phase 1 database.
Can be run with:
    python tests/test_api.py
or
    python -m unittest discover tests
===============================================================================
"""

import sys
import os
import unittest

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app


class TestNWISBackendAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # -------------------------------------------------------------------------
    # 1. Health Checks
    # -------------------------------------------------------------------------
    def test_01_service_health(self):
        """Verify service health endpoint responds with 200 and healthy status."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "NWIS Backend")

    def test_02_database_health(self):
        """Verify database health endpoint can reach PostgreSQL."""
        response = self.client.get("/api/health/db")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "connected")
        self.assertTrue(data["reachable"])

    # -------------------------------------------------------------------------
    # 2. Wells Endpoints
    # -------------------------------------------------------------------------
    def test_03_get_wells(self):
        """Verify GET /api/wells returns all 25 wells."""
        response = self.client.get("/api/wells")
        self.assertEqual(response.status_code, 200)
        wells = response.json()
        self.assertIsInstance(wells, list)
        self.assertEqual(len(wells), 25)
        self.assertEqual(wells[0]["well_name"], "NWIS-W001")

    def test_04_get_wells_with_filter(self):
        """Verify filtering wells by status works."""
        response = self.client.get("/api/wells?status=COMPLETED")
        self.assertEqual(response.status_code, 200)
        wells = response.json()
        self.assertGreater(len(wells), 0)
        for w in wells:
            self.assertIn("COMPLETED", w["status"].upper())

    def test_05_get_well_by_id(self):
        """Verify GET /api/wells/{id} returns single well details."""
        response = self.client.get("/api/wells/1")
        self.assertEqual(response.status_code, 200)
        well = response.json()
        self.assertEqual(well["id"], 1)
        self.assertEqual(well["well_name"], "NWIS-W001")
        self.assertIn("total_depth", well)
        self.assertIn("latitude", well)

    def test_06_get_invalid_well_id(self):
        """Verify requesting non-existent well returns 404 with clean message."""
        response = self.client.get("/api/wells/9999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"].lower())

    # -------------------------------------------------------------------------
    # 3. Nearby Wells (Haversine Distance Search)
    # -------------------------------------------------------------------------
    def test_07_nearby_wells(self):
        """Verify nearby wells returns offset wells ordered by Haversine distance."""
        # Demo cluster center in Demo-Dihing Basin
        response = self.client.get("/api/wells/nearby?lat=27.35&long=95.38&radius=10.0")
        self.assertEqual(response.status_code, 200)
        nearby = response.json()
        self.assertIsInstance(nearby, list)
        self.assertGreater(len(nearby), 0)

        # Ensure results have distance_km and are sorted ascending
        distances = [w["distance_km"] for w in nearby]
        self.assertEqual(distances, sorted(distances))
        for d in distances:
            self.assertLessEqual(d, 10.0)
        self.assertIn("well_id", nearby[0])
        self.assertIn("well_name", nearby[0])

    def test_08_nearby_wells_invalid_radius(self):
        """Verify invalid radius (<=0) returns validation error 422."""
        response = self.client.get("/api/wells/nearby?lat=27.35&long=95.38&radius=-5")
        self.assertEqual(response.status_code, 422)

    def test_09_nearby_wells_invalid_coordinates(self):
        """Verify invalid latitude (>90) returns validation error 422."""
        response = self.client.get("/api/wells/nearby?lat=120.0&long=95.38&radius=10")
        self.assertEqual(response.status_code, 422)

    # -------------------------------------------------------------------------
    # 4. Formations Endpoints
    # -------------------------------------------------------------------------
    def test_10_get_formations_summary(self):
        """Verify GET /api/formations returns distinct formations summary."""
        response = self.client.get("/api/formations")
        self.assertEqual(response.status_code, 200)
        formations = response.json()
        self.assertGreaterEqual(len(formations), 5)
        names = [f["formation_name"] for f in formations]
        self.assertIn("Demo-Barail", names)
        self.assertIn("Demo-Tipam Sandstone", names)

    def test_11_get_well_formations(self):
        """Verify GET /api/wells/{id}/formations returns stratigraphic layers."""
        response = self.client.get("/api/wells/1/formations")
        self.assertEqual(response.status_code, 200)
        layers = response.json()
        self.assertTrue(4 <= len(layers) <= 7)
        # Layers should be sorted by top_depth
        top_depths = [layer["top_depth"] for layer in layers]
        self.assertEqual(top_depths, sorted(top_depths))

    # -------------------------------------------------------------------------
    # 5. Historical Events Endpoints
    # -------------------------------------------------------------------------
    def test_12_get_events(self):
        """Verify GET /api/events returns incidents and supports filtering."""
        response = self.client.get("/api/events")
        self.assertEqual(response.status_code, 200)
        events = response.json()
        self.assertGreater(len(events), 0)
        self.assertIn("event_type", events[0])
        self.assertIn("severity", events[0])

    def test_13_get_events_filtered(self):
        """Verify filtering by event_type (MUD_LOSS)."""
        response = self.client.get("/api/events?event_type=MUD_LOSS")
        self.assertEqual(response.status_code, 200)
        events = response.json()
        self.assertGreater(len(events), 0)
        for e in events:
            self.assertEqual(e["event_type"], "MUD_LOSS")

    def test_14_get_well_history(self):
        """Verify GET /api/wells/{id}/history returns timeline for well."""
        response = self.client.get("/api/wells/2/history")
        self.assertEqual(response.status_code, 200)
        history = response.json()
        self.assertGreater(len(history), 0)
        event_types = [h["event_type"] for h in history]
        self.assertIn("MUD_LOSS", event_types)

    def test_15_get_single_event(self):
        """Verify GET /api/events/{id} returns details for single event."""
        response = self.client.get("/api/events/1")
        self.assertEqual(response.status_code, 200)
        event = response.json()
        self.assertEqual(event["id"], 1)
        self.assertIn("description", event)

    def test_16_get_invalid_event_id(self):
        """Verify non-existent event ID returns 404."""
        response = self.client.get("/api/events/99999")
        self.assertEqual(response.status_code, 404)

    # -------------------------------------------------------------------------
    # 6. Telemetry Endpoints
    # -------------------------------------------------------------------------
    def test_17_get_well_telemetry(self):
        """Verify GET /api/wells/{id}/telemetry returns sensor parameters."""
        response = self.client.get("/api/wells/4/telemetry?limit=50")
        self.assertEqual(response.status_code, 200)
        telemetry = response.json()
        self.assertGreater(len(telemetry), 0)
        self.assertLessEqual(len(telemetry), 50)
        record = telemetry[0]
        self.assertIn("torque", record)
        self.assertIn("measured_depth", record)
        self.assertIn("standpipe_pressure", record)

    def test_18_telemetry_invalid_depth_range(self):
        """Verify start_depth > end_depth returns 400 error."""
        response = self.client.get("/api/wells/4/telemetry?start_depth=3500&end_depth=2000")
        self.assertEqual(response.status_code, 400)
        self.assertIn("start_depth cannot be greater than end_depth", response.json()["detail"])

    def test_19_active_simulated_telemetry(self):
        """Verify GET /api/wells/active/telemetry returns simulated active parameters."""
        response = self.client.get("/api/wells/active/telemetry")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_simulated"])
        self.assertIn("well_id", data)
        self.assertIn("well_name", data)
        self.assertIn("torque", data)
        self.assertIn("measured_depth", data)
        self.assertIn("disclaimer", data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
