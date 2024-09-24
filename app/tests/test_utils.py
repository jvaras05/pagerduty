import unittest
from unittest.mock import patch, AsyncMock
import asyncio
from flask import Flask
from app.utils import fetch_and_store_all_data
from app.extensions import db
import os

class TestUtils(unittest.TestCase):
    """Test cases for utility functions defined in utils.py"""

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("app.utils.fetch_and_store_services", new_callable=AsyncMock)
    @patch("app.utils.fetch_and_store_incidents", new_callable=AsyncMock)
    @patch("app.utils.fetch_and_store_teams", new_callable=AsyncMock)
    @patch("app.utils.fetch_and_store_escalation_policies", new_callable=AsyncMock)
    def test_fetch_and_store_all_data(
        self, mock_services, mock_incidents, mock_teams, mock_policies
    ):
        asyncio.run(fetch_and_store_all_data())
        mock_services.assert_called_once()
        mock_incidents.assert_called_once()
        mock_teams.assert_called_once()
        mock_policies.assert_called_once()


if __name__ == "__main__":
    unittest.main()
