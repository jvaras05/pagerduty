import unittest
from flask import Flask
from unittest.mock import patch, AsyncMock
from app.api import api_blueprint
from app.extensions import db
import os

class TestApiBlueprint(unittest.TestCase):
    """Test cases for all API endpoints in api.py"""

    def setUp(self):
        """Set up a test client for the Flask application and patch the database models."""
        self.app = Flask(__name__)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        # Initialize db
        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Register blueprint
        self.app.register_blueprint(api_blueprint, url_prefix="/api")

        # Patching the models and database
        self.patcher_service = patch("app.models.Service")
        self.patcher_incident = patch("app.models.Incident")
        self.patcher_team = patch("app.models.Team")
        self.patcher_policy = patch("app.models.EscalationPolicy")
        self.MockService = self.patcher_service.start()
        self.MockIncident = self.patcher_incident.start()
        self.MockTeam = self.patcher_team.start()
        self.MockPolicy = self.patcher_policy.start()

    def tearDown(self):
        self.patcher_service.stop()
        self.patcher_incident.stop()
        self.patcher_team.stop()
        self.patcher_policy.stop()
        self.app_context.pop()

    def test_number_of_services(self):
        """Test the /number_of_services API endpoint."""
        self.MockService.query.count.return_value = 5
        response = self.client.get("/api/number_of_services")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"number_of_services": 7})

    def test_incidents_per_service(self):
        """Test the /incidents_per_service API endpoint."""
        self.MockIncident.query.join.return_value.group_by.return_value.all.return_value = [
            ("Service 1", 10),
            ("Service 2", 5),
        ]
        response = self.client.get("/api/incidents_per_service")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json,
            {
                "incidents_per_service": {
                    "03": 5,
                    "CSG Infra provisioning": 3,
                    "Healthcheck Support": 3,
                    "Service 01": 4,
                    "Service 02": 3,
                    "Service 04": 4,
                    "Service 5": 3,
                }
            },
        )

    @patch("app.api.fetch_data", new_callable=AsyncMock)
    def test_fetch_and_store_data(self, mock_fetch_and_store_all_data):
        """Test the /fetch_data API endpoint."""
        response = self.client.post("/api/fetch_data")
        self.assertEqual(response.status_code, 200)

    def test_generate_report(self):
        """Test the /generate_report API endpoint."""
        response = self.client.get("/api/generate_report")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
