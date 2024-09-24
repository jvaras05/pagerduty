import requests
from app.models import *
import asyncio
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import os

# API configuration
PAGERDUTY_API_KEY = os.getenv("PAGERDUTY_API_KEY")
BASE_URL = os.getenv("BASE_URL")

headers = {
    "Authorization": f"Token token={PAGERDUTY_API_KEY}",
    "Accept": "application/vnd.pagerduty+json;version=2",
}


async def fetch_data(endpoint):
    """Helper function to fetch data from PagerDuty API."""
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from {endpoint}: {e}")
        return None


async def fetch_and_store_services():
    """Fetch and store services from PagerDuty."""
    data = await fetch_data("services")
    if data and "services" in data:
        for service_data in data["services"]:
            service = Service.query.get(service_data["id"]) or Service(
                id=service_data["id"]
            )
            service.name = service_data["name"]
            service.description = service_data.get("description")
            service.created_at = datetime.strptime(
                service_data.get("created_at"), "%Y-%m-%dT%H:%M:%S%z"
            )
            service.updated_at = datetime.strptime(
                service_data.get("updated_at"), "%Y-%m-%dT%H:%M:%S%z"
            )
            service.status = service_data.get("status")
            service.html_url = service_data.get("html_url")

            # Handle the many-to-many relationship with teams
            service.teams = []  # Clear existing teams
            for team_data in service_data["teams"]:
                team = Team.query.get(team_data["id"]) or Team(id=team_data["id"])
                team.name = team_data.get("summary", team_data["id"])
                team.html_url = team_data.get("html_url")
                service.teams.append(team)

            # Save or update the service in the database
            db.session.merge(service)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error saving services to DB: {e}")


async def fetch_and_store_incidents():
    """Fetch and store incidents from PagerDuty."""
    data = await fetch_data("incidents")
    if data and "incidents" in data:
        for incident_data in data["incidents"]:
            incident = (
                Incident.query.filter_by(
                    incident_number=incident_data["incident_number"]
                ).first()
                or Incident()
            )
            incident.id = incident_data["incident_key"]
            incident.incident_number = incident_data["incident_number"]
            incident.title = incident_data["title"]
            incident.description = incident_data.get("description")
            incident.status = incident_data["status"]
            incident.created_at = datetime.strptime(
                incident_data["created_at"], "%Y-%m-%dT%H:%M:%SZ"
            )
            incident.updated_at = datetime.strptime(
                incident_data["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
            )
            service_data = incident_data.get("service")
            if service_data:
                service = Service.query.get(service_data["id"])
                if service:
                    incident.service = service

            # Save to database
            db.session.merge(incident)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error saving incidents to DB: {e}")


async def fetch_and_store_teams():
    """Fetch and store teams from PagerDuty."""
    data = await fetch_data("teams")
    if data and "teams" in data:
        for team_data in data["teams"]:
            team = Team.query.get(team_data["id"]) or Team(id=team_data["id"])
            team.name = team_data["name"]
            team.summary = team_data.get("summary")
            team.html_url = team_data.get("html_url")

            # Save to database
            db.session.merge(team)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error saving teams to DB: {e}")


async def fetch_and_store_escalation_policies():
    """Fetch and store escalation policies from PagerDuty."""
    data = await fetch_data("escalation_policies")
    if data and "escalation_policies" in data:
        for policy_data in data["escalation_policies"]:
            policy = EscalationPolicy.query.get(policy_data["id"]) or EscalationPolicy(
                id=policy_data["id"]
            )
            policy.name = policy_data["name"]
            policy.summary = policy_data["summary"]
            policy.description = policy_data.get("description")

            # Save to database
            db.session.merge(policy)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error saving escalation policies to DB: {e}")


async def fetch_and_store_all_data():
    """Fetch and store all data from PagerDuty."""
    await asyncio.gather(
        fetch_and_store_services(),
        fetch_and_store_incidents(),
        fetch_and_store_teams(),
        fetch_and_store_escalation_policies(),
    )
