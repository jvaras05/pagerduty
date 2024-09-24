import os
import logging
from flask import Flask
from app.extensions import db
from app.api import api_blueprint
from app.models import *
from sqlalchemy.exc import SQLAlchemyError


def create_app(config=None):
    app = Flask(__name__)
    app.register_blueprint(api_blueprint, url_prefix="/api")
    # Log environment details
    logging.basicConfig(level=logging.DEBUG)
    logging.info(f"Creating app with config: {config}")

    # Load config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True
    logging.info(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    db.init_app(app)

    with app.app_context():
        try:
            logging.info("Creating all tables...")
            db.create_all()
            logging.info("Tables created successfully.")
        except SQLAlchemyError as e:
            logging.error(f"Error during table creation: {e}")
            raise e

    return app
