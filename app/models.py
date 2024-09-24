from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for many-to-many relationship between escalation policies and services
escalation_policy_service = db.Table(
    "escalation_policy_service",
    db.Column(
        "escalation_policy_id",
        db.String(50),
        db.ForeignKey("escalation_policies.id"),
        primary_key=True,
    ),
    db.Column(
        "service_id", db.String(50), db.ForeignKey("services.id"), primary_key=True
    ),
)

# Association table for many-to-many relationship between escalation policies and teams
escalation_policy_team = db.Table(
    "escalation_policy_team",
    db.Column(
        "escalation_policy_id",
        db.String(50),
        db.ForeignKey("escalation_policies.id"),
        primary_key=True,
    ),
    db.Column("team_id", db.String(50), db.ForeignKey("teams.id"), primary_key=True),
)

# Association table for many-to-many relationship between services and teams
service_team = db.Table(
    "service_team",
    db.Column(
        "service_id", db.String(50), db.ForeignKey("services.id"), primary_key=True
    ),
    db.Column("team_id", db.String(50), db.ForeignKey("teams.id"), primary_key=True),
)


class EscalationPolicy(db.Model):
    __tablename__ = "escalation_policies"
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    num_loops = db.Column(db.Integer, nullable=True)
    on_call_handoff_notifications = db.Column(db.String(50), nullable=True)

    # Relationships
    escalation_rules = db.relationship(
        "EscalationRule", backref="escalation_policy", cascade="all, delete-orphan"
    )
    services = db.relationship(
        "Service",
        secondary=escalation_policy_service,
        back_populates="escalation_policies",
    )
    teams = db.relationship(
        "Team", secondary=escalation_policy_team, back_populates="escalation_policies"
    )


class EscalationRule(db.Model):
    __tablename__ = "escalation_rules"
    id = db.Column(db.String(50), primary_key=True)
    escalation_delay_in_minutes = db.Column(db.Integer, nullable=False)
    escalation_policy_id = db.Column(
        db.String(50), db.ForeignKey("escalation_policies.id"), nullable=False
    )

    # Relationships
    targets = db.relationship(
        "Target", backref="escalation_rule", cascade="all, delete-orphan"
    )


class Target(db.Model):
    __tablename__ = "targets"
    id = db.Column(db.String(50), primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    summary = db.Column(db.String(255), nullable=False)
    html_url = db.Column(db.String(255), nullable=True)

    escalation_rule_id = db.Column(
        db.String(50), db.ForeignKey("escalation_rules.id"), nullable=False
    )
    user_id = db.Column(
        db.String(50), db.ForeignKey("users.id"), nullable=True
    )  # Added foreign key for User
    schedule_id = db.Column(
        db.String(50), db.ForeignKey("schedules.id"), nullable=True
    )  # Added foreign key for Schedule


class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    html_url = db.Column(db.String(255), nullable=True)

    # Many-to-many relationship with Team
    teams = db.relationship("Team", secondary=service_team, back_populates="services")

    # Many-to-many relationship with EscalationPolicy
    escalation_policies = db.relationship(
        "EscalationPolicy",
        secondary=escalation_policy_service,
        back_populates="services",
    )

    # Relationship with incidents, renamed backref to avoid conflict
    incidents = db.relationship(
        "Incident", backref="related_service", cascade="all, delete-orphan"
    )


class Team(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.String(255))
    html_url = db.Column(db.String(255), nullable=True)

    # Many-to-many relationship with Service
    services = db.relationship(
        "Service", secondary=service_team, back_populates="teams"
    )

    # Many-to-many relationship with EscalationPolicy
    escalation_policies = db.relationship(
        "EscalationPolicy", secondary=escalation_policy_team, back_populates="teams"
    )


class Incident(db.Model):
    __tablename__ = "incidents"
    id = db.Column(db.String(50), primary_key=True)
    incident_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    incident_key = db.Column(db.String(255), nullable=True)

    service_id = db.Column(db.String(50), db.ForeignKey("services.id"), nullable=False)
    # Backref renamed to avoid conflict with incidents
    service = db.relationship("Service", backref="service_incidents")


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    html_url = db.Column(db.String(255), nullable=True)

    # Relationship to target (for escalation rules)
    targets = db.relationship("Target", backref="user")


class Schedule(db.Model):
    __tablename__ = "schedules"
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    html_url = db.Column(db.String(255), nullable=True)

    # Relationship to target (for escalation rules)
    targets = db.relationship("Target", backref="schedule")
