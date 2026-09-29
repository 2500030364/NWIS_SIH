"""
===============================================================================
NWIS Backend - Phase 4 Smart Risk Engine & Alerts Test Suite
===============================================================================
Validates:
1. Formation alignment across stratigraphic depths
2. Approaching a historical mud-loss zone (Demo-Barail ~3020m)
3. Approaching a historical stuck-pipe zone (Demo-Kopili ~3520m)
4. Safe depth interval far from historical events (Demo-Alluvium ~500m)
5. Telemetry anomaly pattern detection
6. Explainability output (supporting wells, depth intervals, narratives)
7. REST APIs:
   - GET /api/risks/{well_id}
   - GET /api/alerts/{well_id}
   - GET /api/wells/active/state
   - POST /api/wells/active/set_depth
   - POST /api/wells/active/step
===============================================================================
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.services.risk_engine import RiskEngine


class TestSmartRiskEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()
        cls.engine = RiskEngine(cls.db)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_formation_alignment(self):
        """Test formation alignment across different depths for well 1."""
        form_name, bounds = self.engine.get_formation_for_depth(1, 500.0)
        self.assertIn("Alluvium", form_name)

        form_name, bounds = self.engine.get_formation_for_depth(1, 1200.0)
        self.assertIn("Girujan", form_name)

        form_name, bounds = self.engine.get_formation_for_depth(1, 2000.0)
        self.assertIn("Tipam", form_name)

        form_name, bounds = self.engine.get_formation_for_depth(1, 3020.0)
        self.assertEqual(form_name, "Demo-Barail")

        form_name, bounds = self.engine.get_formation_for_depth(1, 3500.0)
        self.assertEqual(form_name, "Demo-Kopili Shale")

    def test_02_mud_loss_zone_risk(self):
        """At 3020m in Demo-Barail, mud loss risk must be elevated with offset well evidence."""
        assessment = self.engine.evaluate_well_risks(1, target_depth=3020.0, radius_km=25.0)
        self.assertEqual(assessment.current_formation, "Demo-Barail")
        self.assertEqual(assessment.current_depth, 3020.0)

        # Find MUD_LOSS assessment
        mud_loss_risk = next((r for r in assessment.risks if r.risk_type == "MUD_LOSS"), None)
        self.assertIsNotNone(mud_loss_risk)
        self.assertIn(mud_loss_risk.level, ["HIGH", "CRITICAL"])
        self.assertGreaterEqual(mud_loss_risk.score, 0.50)

        # Verify supporting wells include known synthetic offset wells
        self.assertTrue(any(w in mud_loss_risk.supporting_wells for w in ["NWIS-W002", "NWIS-W007", "NWIS-W011", "NWIS-W015", "NWIS-W019"]))
        self.assertIn("3040", mud_loss_risk.historical_depth_interval)
        self.assertIn("Potential Mud Loss Risk", mud_loss_risk.title)
        self.assertIn("Demo-Barail", mud_loss_risk.explanation)
        self.assertIsNotNone(mud_loss_risk.recommended_mitigation)

    def test_03_stuck_pipe_zone_risk(self):
        """At 3520m in Demo-Kopili Shale, stuck pipe risk must be elevated with offset well evidence."""
        assessment = self.engine.evaluate_well_risks(1, target_depth=3520.0, radius_km=25.0)
        self.assertEqual(assessment.current_formation, "Demo-Kopili Shale")

        stuck_pipe_risk = next((r for r in assessment.risks if r.risk_type == "STUCK_PIPE"), None)
        self.assertIsNotNone(stuck_pipe_risk)
        self.assertIn(stuck_pipe_risk.level, ["HIGH", "CRITICAL"])
        self.assertGreaterEqual(stuck_pipe_risk.score, 0.50)
        self.assertTrue(any(w in stuck_pipe_risk.supporting_wells for w in ["NWIS-W004", "NWIS-W008", "NWIS-W014", "NWIS-W022"]))

    def test_04_safe_depth_interval(self):
        """At 300m in shallow formation, risks should be LOW."""
        assessment = self.engine.evaluate_well_risks(1, target_depth=300.0, radius_km=25.0)
        # All severe risks should be LOW at 300m
        for r in assessment.risks:
            self.assertIn(r.level, ["LOW", "MEDIUM"])
            self.assertLess(r.score, 0.60)

    def test_05_telemetry_pattern_detection(self):
        """Telemetry pattern helper correctly flags real and simulated sensor anomalies."""
        # Test real database mud-flow drop signature in NWIS-W002 at 2976m
        insights_w2 = self.engine.analyze_telemetry_patterns(2, 2976.0)
        self.assertTrue(insights_w2["anomaly_found"])
        self.assertEqual(insights_w2["mud_flow_trend"], "DECREASING")

        # Test real database torque escalation signature in NWIS-W004 at 3520m
        insights_w4 = self.engine.analyze_telemetry_patterns(4, 3520.0)
        self.assertTrue(insights_w4["anomaly_found"])
        self.assertEqual(insights_w4["torque_trend"], "INCREASING")

    def test_06_api_get_risks(self):
        """Verify GET /api/risks/{well_id} endpoint."""
        response = self.client.get("/api/risks/1?depth=3020.0")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["well_id"], 1)
        self.assertEqual(data["current_formation"], "Demo-Barail")
        self.assertGreater(data["total_risks_assessed"], 0)
        self.assertIn("risks", data)
        self.assertIn("disclaimer", data)

    def test_07_api_get_alerts(self):
        """Verify GET /api/alerts/{well_id} filters to actionable alerts."""
        response = self.client.get("/api/alerts/1?depth=3020.0&min_level=MEDIUM")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("alerts", data)
        self.assertGreaterEqual(len(data["alerts"]), 1)
        # Ensure only MEDIUM, HIGH, CRITICAL exist
        for alert in data["alerts"]:
            self.assertIn(alert["level"], ["MEDIUM", "HIGH", "CRITICAL"])

    def test_08_api_active_well_state_and_stepping(self):
        """Verify active well state and interactive depth control."""
        # Set depth to 3020m
        set_resp = self.client.post("/api/wells/active/set_depth?depth=3020.0&well_id=1")
        self.assertEqual(set_resp.status_code, 200)
        self.assertEqual(set_resp.json()["current_depth"], 3020.0)

        # Get state
        state_resp = self.client.get("/api/wells/active/state?well_id=1")
        self.assertEqual(state_resp.status_code, 200)
        state_data = state_resp.json()
        self.assertEqual(state_data["current_depth"], 3020.0)
        self.assertEqual(state_data["current_formation"], "Demo-Barail")
        self.assertGreaterEqual(state_data["active_alerts"], 1)

        # Advance step by +10m
        step_resp = self.client.post("/api/wells/active/step?delta_m=10.0&well_id=1")
        self.assertEqual(step_resp.status_code, 200)
        self.assertEqual(step_resp.json()["current_depth"], 3030.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
