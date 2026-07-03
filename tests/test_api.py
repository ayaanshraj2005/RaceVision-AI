import sys
import os
import unittest
from fastapi.testclient import TestClient

# Adjust path to import src module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app

class TestRaceVisionAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Mock valid driver entry
        cls.valid_driver = {
            "driver_id": 1,
            "driver_name": "Lewis Hamilton",
            "constructor_id": 131,
            "constructor_name": "Mercedes",
            "grid": 1,
            "driver_age": 36.2,
            "driver_experience": 266,
            "driver_recent_form": 2.2,
            "driver_rolling_grid": 1.8,
            "driver_avg_finish": 3.4,
            "driver_consistency": 4.1,
            "driver_win_rate": 0.35,
            "driver_podium_rate": 0.61,
            "driver_top10_rate": 0.88,
            "driver_dnf_rate": 0.08,
            "grid_delta_to_avg": -0.8,
            "constructor_strength_index": 39.7,
            "circuit_familiarity": 14,
            "circuit_grid_importance": 0.60,
            "is_home_race": 0
        }
        # Mock race payload
        cls.valid_payload = {
            "race_id": 1051,
            "entries": [cls.valid_driver]
        }

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
        print(" [PASS] GET /health")

    def test_version_check(self):
        response = self.client.get("/version")
        self.assertEqual(response.status_code, 200)
        self.assertIn("version", response.json())
        print(" [PASS] GET /version")

    def test_model_information(self):
        response = self.client.get("/model/information")
        self.assertEqual(response.status_code, 200)
        self.assertIn("regressor_algorithm", response.json())
        self.assertIn("features_used", response.json())
        print(" [PASS] GET /model/information")

    def test_model_metrics(self):
        response = self.client.get("/model/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertIn("regression_metrics", response.json())
        self.assertIn("classification_metrics", response.json())
        print(" [PASS] GET /model/metrics")

    def test_feature_importance(self):
        response = self.client.get("/explain/feature-importance")
        self.assertEqual(response.status_code, 200)
        self.assertIn("feature_importance", response.json())
        print(" [PASS] GET /explain/feature-importance")

    def test_explain_prediction(self):
        payload = {
            "driver_name": "Lewis Hamilton",
            "constructor_name": "Mercedes",
            "grid": 1,
            "driver_recent_form": 2.2,
            "constructor_strength_index": 39.7,
            "grid_delta_to_avg": -0.8,
            "circuit_grid_importance": 0.60,
            "circuit_name": "Monaco GP"
        }
        response = self.client.post("/explain/prediction", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("explanation", response.json())
        self.assertIn("predicted_finishing_position", response.json())
        print(" [PASS] POST /explain/prediction")

    def test_predict_finish_position(self):
        response = self.client.post("/predict/finish-position", json=self.valid_payload)
        self.assertEqual(response.status_code, 200)
        predictions = response.json()["predictions"]
        self.assertTrue(len(predictions) > 0)
        self.assertIn("predicted_finishing_position", predictions[0])
        print(" [PASS] POST /predict/finish-position")

    def test_predict_podium_probability(self):
        response = self.client.post("/predict/podium-probability", json=self.valid_payload)
        self.assertEqual(response.status_code, 200)
        predictions = response.json()["predictions"]
        self.assertIn("predicted_podium_probability", predictions[0])
        print(" [PASS] POST /predict/podium-probability")

    def test_predict_driver_performance(self):
        response = self.client.post("/predict/driver-performance", json=self.valid_payload)
        self.assertEqual(response.status_code, 200)
        predictions = response.json()["predictions"]
        self.assertIn("driver_performance_score", predictions[0])
        print(" [PASS] POST /predict/driver-performance")

    def test_predict_team_performance(self):
        response = self.client.post("/predict/team-performance", json=self.valid_payload)
        self.assertEqual(response.status_code, 200)
        predictions = response.json()["predictions"]
        self.assertIn("team_performance_score", predictions[0])
        print(" [PASS] POST /predict/team-performance")

    def test_analytics_dashboard(self):
        response = self.client.get("/analytics/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_races", response.json())
        self.assertIn("seasons_covered", response.json())
        print(" [PASS] GET /analytics/dashboard")

    def test_analytics_drivers(self):
        response = self.client.get("/analytics/drivers")
        self.assertEqual(response.status_code, 200)
        drivers = response.json()
        self.assertTrue(len(drivers) > 0)
        # Test individual lookup
        first_driver_id = drivers[0]["driver_id"]
        resp_single = self.client.get(f"/analytics/drivers/{first_driver_id}")
        self.assertEqual(resp_single.status_code, 200)
        print(" [PASS] GET /analytics/drivers & /analytics/drivers/{id}")

    def test_analytics_teams(self):
        response = self.client.get("/analytics/teams")
        self.assertEqual(response.status_code, 200)
        teams = response.json()
        self.assertTrue(len(teams) > 0)
        # Test individual lookup
        first_team_id = teams[0]["constructor_id"]
        resp_single = self.client.get(f"/analytics/teams/{first_team_id}")
        self.assertEqual(resp_single.status_code, 200)
        print(" [PASS] GET /analytics/teams & /analytics/teams/{id}")

    def test_analytics_circuits(self):
        response = self.client.get("/analytics/circuits")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
        print(" [PASS] GET /analytics/circuits")

    def test_analytics_seasons(self):
        response = self.client.get("/analytics/seasons")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
        print(" [PASS] GET /analytics/seasons")

    def test_validation_handling(self):
        # Send empty entries -> should return validation error (422)
        invalid_payload = {
            "race_id": 1051,
            "entries": []
        }
        response = self.client.post("/predict/finish-position", json=invalid_payload)
        self.assertEqual(response.status_code, 422)
        
        # Send grid out of bounds -> should return validation error (422)
        bad_grid_entry = self.valid_driver.copy()
        bad_grid_entry["grid"] = 99
        bad_payload = {"race_id": 1051, "entries": [bad_grid_entry]}
        response_bad = self.client.post("/predict/finish-position", json=bad_payload)
        self.assertEqual(response_bad.status_code, 422)

        # Send mismatched driver and team name -> should return 400 Bad Request
        mismatch_payload = {
            "driver_name": "Max Verstappen",
            "constructor_name": "Mercedes",
            "grid": 1,
            "driver_recent_form": 2.2,
            "constructor_strength_index": 39.7,
            "grid_delta_to_avg": -0.8,
            "circuit_grid_importance": 0.60,
            "circuit_name": "Monaco GP"
        }
        response_mismatch = self.client.post("/explain/prediction", json=mismatch_payload)
        self.assertEqual(response_mismatch.status_code, 400)
        self.assertIn("has no record of driving for team", response_mismatch.json()["detail"])
        print(" [PASS] Request Validation, 422 Rejection & 400 XAI Mismatch Rejection")

if __name__ == "__main__":
    print("\n--- Initializing RaceVision API Testing Suite ---\n")
    unittest.main()
