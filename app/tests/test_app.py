import unittest
from unittest.mock import patch
from flask import Flask
from app.extensions import db
import os

class TestAppInitialization(unittest.TestCase):
    """Test cases for Flask app initialization in __init__.py"""

    @patch("app.extensions.db.init_app")
    def test_create_app(self, mock_init_app):
        """Test the app initialization, configuration, and blueprint registration."""
        from app import create_app

        app = create_app()

        # Assert that the app is a Flask instance
        self.assertIsInstance(app, Flask)

        # Test if the app has the right configuration values
        self.assertEqual(
            app.config["SQLALCHEMY_DATABASE_URI"], os.getenv("SQLALCHEMY_DATABASE_URI")
        )
        self.assertFalse(app.config["SQLALCHEMY_TRACK_MODIFICATIONS"])
        self.assertTrue(app.config["SQLALCHEMY_ECHO"])

        # Test if the API blueprint was registered
        self.assertIn("api", app.blueprints)


if __name__ == "__main__":
    unittest.main()
