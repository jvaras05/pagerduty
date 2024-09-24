from flask import Blueprint, jsonify, make_response, send_file
from app.models import Service, Incident, Team, EscalationPolicy, User, Schedule
from app.utils import fetch_and_store_all_data
from app.extensions import db
import asyncio
import csv
import matplotlib.pyplot as plt
import io
from io import BytesIO

# Define the blueprint for the API routes
api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/number_of_services", methods=["GET"])
def number_of_services():
    """
    Fetches the total number of services.

    Returns:
        JSON response with the number of services in the database.
    """
    count = Service.query.count()
    return jsonify({"number_of_services": count})


@api_blueprint.route("/incidents_per_service", methods=["GET"])
def incidents_per_service():
    """
    Fetches the number of incidents per service.

    Returns:
        JSON response with the number of incidents for each service.
    """
    results = (
        db.session.query(Service.name, db.func.count(Incident.id))
        .join(Incident, Incident.service_id == Service.id)
        .group_by(Service.name)
        .all()
    )
    return jsonify({"incidents_per_service": dict(results)})


@api_blueprint.route("/incidents_by_service_and_status", methods=["GET"])
def incidents_by_service_and_status():
    """
    Fetches the number of incidents grouped by service and status.

    Returns:
        JSON response with incidents count per service and status.
    """
    results = (
        db.session.query(Service.name, Incident.status, db.func.count(Incident.id))
        .join(Incident, Incident.service_id == Service.id)
        .group_by(Service.name, Incident.status)
        .all()
    )
    return jsonify(
        {
            "incidents_by_service_and_status": [
                {"service": row[0], "status": row[1], "count": row[2]}
                for row in results
            ]
        }
    )


@api_blueprint.route("/teams_and_services", methods=["GET"])
def teams_and_services():
    """
    Fetches the number of services per team.

    Returns:
        JSON response with the count of services associated with each team.
    """
    results = (
        db.session.query(Team.name, db.func.count(Service.id))
        .join(Service, Service.teams.any(Team.id == Team.id))
        .group_by(Team.name)
        .all()
    )
    return jsonify(
        {
            "teams_and_services": [
                {"team": row[0], "services_count": row[1]} for row in results
            ]
        }
    )


@api_blueprint.route("/generate_report", methods=["GET"])
def generate_csv_report():
    """
    Generates a CSV report of the number of incidents per service.

    Returns:
        CSV file as an attachment in the HTTP response.
    """
    results = (
        db.session.query(
            Service.name, db.func.count(Incident.id).label("incident_count")
        )
        .join(Incident)
        .group_by(Service.name)
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Service", "Number of Incidents"])

    for row in results:
        writer.writerow([row[0], row[1]])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=report.csv"
    response.headers["Content-type"] = "text/csv"

    return response


@api_blueprint.route("/service_with_most_incidents", methods=["GET"])
def service_with_most_incidents():
    """
    Fetches the service with the most incidents.

    Returns:
        JSON response with the service that has the most incidents and the number of incidents.
    """
    results = (
        db.session.query(
            Service.name, db.func.count(Incident.id).label("incident_count")
        )
        .join(Incident, Incident.service_id == Service.id)
        .group_by(Service.name)
        .order_by(db.func.count(Incident.id).desc())
        .first()
    )
    return jsonify(
        {"service_with_most_incidents": results[0], "incident_count": results[1]}
    )


@api_blueprint.route("/incidents_graph", methods=["GET"])
def incidents_graph():
    """
    Generates a bar chart of incidents per service.

    Returns:
        An image file (PNG format) with the bar chart.
    """
    results = (
        db.session.query(
            Service.name, db.func.count(Incident.id).label("incident_count")
        )
        .join(Incident)
        .group_by(Service.name)
        .all()
    )

    services = [row[0] for row in results]
    incident_counts = [row[1] for row in results]

    plt.figure(figsize=(10, 5))
    plt.bar(services, incident_counts)
    plt.title("Incidents per Service")
    plt.xlabel("Services")
    plt.ylabel("Number of Incidents")

    img = BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)

    return send_file(img, mimetype="image/png")


@api_blueprint.route("/escalation_policies", methods=["GET"])
def escalation_policies():
    """
    Fetches all escalation policies.

    Returns:
        JSON response with all escalation policies.
    """
    results = db.session.query(
        EscalationPolicy.id, EscalationPolicy.name, EscalationPolicy.description
    ).all()
    return jsonify(
        {
            "escalation_policies": [
                {"id": row[0], "name": row[1], "description": row[2]} for row in results
            ]
        }
    )


@api_blueprint.route("/services", methods=["GET"])
def get_services():
    """
    Fetches all services.

    Returns:
        JSON response with all services.
    """
    services = Service.query.all()
    return jsonify([{"id": s.id, "name": s.name} for s in services])


@api_blueprint.route("/incidents", methods=["GET"])
def get_incidents():
    """
    Fetches all incidents.

    Returns:
        JSON response with all incidents.
    """
    incidents = Incident.query.all()
    return jsonify(
        [
            {"id": i.id, "status": i.status, "service_id": i.service_id}
            for i in incidents
        ]
    )


@api_blueprint.route("/teams", methods=["GET"])
def get_teams():
    """
    Fetches all teams.

    Returns:
        JSON response with all teams.
    """
    teams = Team.query.all()
    return jsonify([{"id": t.id, "name": t.name} for t in teams])


@api_blueprint.route("/fetch_data", methods=["POST"])
def fetch_data():
    """
    Fetches and stores all data asynchronously by calling the fetch_and_store_all_data function.

    Returns:
        JSON response with a success message upon completion.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_and_store_all_data())
    return jsonify({"message": "Data fetched and stored successfully"}), 200
