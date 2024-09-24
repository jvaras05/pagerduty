# Pagerduty flask API

## Overview

This project is a Flask-based web application that manages services, incidents, teams, and escalation policies. It provides multiple API endpoints to fetch, visualize, and report data, such as incidents per service, escalation policies, and more.

The application is built using Flask with SQLAlchemy for database interactions. The APIs support fetching and processing incident and service data, generating reports, and visualizing data with graphs.

## Table of Contents

- [Flask Incident Management System](#flask-incident-management-system)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Technologies Used](#technologies-used)
  - [Project Structure](#project-structure)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
  - [Environment Variables](#environment-variables)
  - [Running the Application](#running-the-application)
  - [API Endpoints](#api-endpoints)
  - [Running Tests](#running-tests)
  - [Conclusion](#conclusion)

## Technologies Used

- **Flask**: Web framework.
- **Flask-SQLAlchemy**: ORM for database management.
- **MySQL**: Database system.
- **Matplotlib**: For generating visual graphs.
- **Docker Compose**: For containerizing the app and database.
- **Unittest**: For writing and running test cases.

## Project Structure

```bash
├── app/
│   ├── __init__.py              # Application factory and setup.
│   ├── api.py                   # API blueprint with route definitions.
│   ├── extensions.py            # Extensions (e.g., SQLAlchemy instance).
│   ├── models.py                # Database models for Service, Incident, Team, etc.
│   ├── utils.py                 # Utility functions for data fetching and processing.
│   ├── tests/
│       ├── test_app.py          # Test cases for app initialization.
│       ├── test_api.py          # Test cases for API routes.
│       ├── test_utils.py        # Test cases for utility functions.
├── .env                         # Environment variables.
├── Dockerfile                   # Dockerfile for the web service.
├── docker-compose.yml           # Docker Compose configuration for the app and MySQL database.
```

## Installation

### Prerequisites

Ensure that you have the following installed:

- Docker
- Docker Compose
- Python 3.x

### Steps

1. **Clone the Repository:**

```bash
git clone https://github.com/jvaras05/pagerduty.git
cd pagerduty
```

2. **Create a `.env` File:**  
   In the root of the project, create a `.env` file and specify the necessary environment variables:

```makefile
FLASK_ENV=development
SQLALCHEMY_DATABASE_URI=mysql://root@db/pagerduty_db
MYSQL_ALLOW_EMPTY_PASSWORD=yes
MYSQL_DATABASE=pagerduty_db
```

3. **Build the Docker Containers:**

```bash
docker-compose build
```

4. **Run the Docker Containers:**

```bash
docker-compose up
```

This will start both the web service and the MySQL database.

## Environment Variables

The application uses the following environment variables (stored in `.env`):

- **FLASK_ENV**: Specifies the Flask environment (development/production).
- **SQLALCHEMY_DATABASE_URI**: The database connection URI for SQLAlchemy.
- **MYSQL_ALLOW_EMPTY_PASSWORD**: Allows MySQL to have an empty root password.
- **MYSQL_DATABASE**: The name of the MySQL database to be created.

## Running the Application

After running `docker-compose up`, the web application should be running on port `5000`. You can access the APIs using the following base URL:

```bash
http://localhost:5000/api
```

## API Endpoints

1. **GET /api/number_of_services**  
   Fetches the total number of services.  
   **Response**: JSON object with the number of services.

2. **GET /api/incidents_per_service**  
   Fetches the number of incidents per service.  
   **Response**: JSON object with the count of incidents for each service.

3. **GET /api/incidents_by_service_and_status**  
   Fetches incidents grouped by service and status.  
   **Response**: JSON array with the count of incidents per service and status.

4. **GET /api/teams_and_services**  
   Fetches the number of services per team.  
   **Response**: JSON array with the count of services for each team.

5. **GET /api/generate_report**  
   Generates a CSV report of incidents per service.  
   **Response**: CSV file containing the data.

6. **GET /api/service_with_most_incidents**  
   Fetches the service with the highest number of incidents.  
   **Response**: JSON object with the service and incident count.

7. **GET /api/incidents_graph**  
   Generates a bar chart of incidents per service.  
   **Response**: PNG image containing the bar chart.

8. **POST /api/fetch_data**  
   Asynchronously fetches and stores all incident, service, team, and policy data.  
   **Response**: Success message.

## Running Tests

This project uses the `unittest` framework to write and run test cases for app initialization, API routes, and utility functions.

To run all test cases:

1. **Ensure that the Docker containers are up and running:**

```bash
docker-compose up
```

2. **Run the tests:**
   Inside the Docker container or in the root directory of the project, run:

```bash
docker exec -it <container_id> bash
python -m unittest discover tests
```

Alternatively, run locally:

```bash
python -m unittest discover app/tests
```

## Conclusion

This project provides a robust API for managing services, incidents, and teams with additional features like reporting and data visualization. By using Docker, the application is easily containerized and can be set up in any environment with minimal configuration.
