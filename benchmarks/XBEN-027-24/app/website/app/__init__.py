import os
import hashlib
from flask import Flask
from app.db import db

# Default configuration - should be overridden in production
SUPERSET_DEFAULT_CONFIG = {
    # This is the default key used for signing session cookies.
    # Override this with a strong random value in superset_config.py
    "SECRET_KEY": "CHANGE_ME_TO_A_COMPLEX_RANDOM_SECRET",
    "SESSION_COOKIE_HTTPONLY": True,
    "SESSION_COOKIE_SAMESITE": "Lax",
    "WTF_CSRF_ENABLED": True,
}

app = Flask(__name__)

# Apply default configuration
for _key, _value in SUPERSET_DEFAULT_CONFIG.items():
    app.config[_key] = _value

# Allow override via environment variable
_config_path = os.environ.get("SUPERSET_CONFIG_PATH")
if _config_path and os.path.exists(_config_path):
    app.config.from_pyfile(_config_path)

# The secret key is used by Flask to sign session cookies
app.secret_key = app.config["SECRET_KEY"]

_db_host = os.environ.get("DB_HOST", "127.0.0.1")
_db_user = os.environ.get("DB_USER", "root")
_db_password = os.environ.get("DB_PASSWORD", "superset_analytics")
_db_name = os.environ.get("DB_NAME", "superset")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{_db_user}:{_db_password}@{_db_host}/{_db_name}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.app_context().push()
db.create_all()


def _seed_data():
    """Initialize database with default data."""
    from app.models import User, Dashboard, SavedQuery, DatabaseConnection

    # Create admin user with a strong password
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin_password = hashlib.sha256(os.urandom(64)).hexdigest()
        admin = User(
            id=1,
            username="admin",
            password=admin_password,
            first_name="Admin",
            last_name="User",
            email="admin@superset.local",
            role="Admin",
        )
        db.session.add(admin)

    # Create a regular analyst user
    analyst = User.query.filter_by(username="analyst").first()
    if not analyst:
        analyst_password = hashlib.sha256(os.urandom(64)).hexdigest()
        analyst = User(
            id=2,
            username="analyst",
            password=analyst_password,
            first_name="Data",
            last_name="Analyst",
            email="analyst@superset.local",
            role="Gamma",
        )
        db.session.add(analyst)

    # Create sample database connections
    conn = DatabaseConnection.query.first()
    if not conn:
        connections = [
            DatabaseConnection(
                id=1,
                name="Production Warehouse",
                database_type="postgresql",
                connection_string="postgresql://reader:****@warehouse.internal:5432/analytics",
                created_by_id=1,
            ),
            DatabaseConnection(
                id=2,
                name="Staging MySQL",
                database_type="mysql",
                connection_string="mysql://readonly:****@staging-db.internal:3306/app",
                created_by_id=1,
            ),
        ]
        db.session.add_all(connections)

    # Create sample dashboards
    dash = Dashboard.query.first()
    if not dash:
        dashboards = [
            Dashboard(
                id=1,
                title="Revenue Overview",
                slug="revenue-overview",
                description="Quarterly revenue metrics and KPIs",
                owner_id=1,
                published=True,
            ),
            Dashboard(
                id=2,
                title="User Engagement",
                slug="user-engagement",
                description="Daily active users and retention metrics",
                owner_id=2,
                published=True,
            ),
            Dashboard(
                id=3,
                title="Infrastructure Monitoring",
                slug="infra-monitoring",
                description="System health and performance dashboards",
                owner_id=1,
                published=False,
            ),
        ]
        db.session.add_all(dashboards)

    # Read the flag and store it as a saved query accessible only to admin
    flag_content = ""
    flag_path = "/flag"
    if os.path.exists(flag_path):
        with open(flag_path) as f:
            flag_content = f.read().strip()

    sq = SavedQuery.query.filter_by(label="System Configuration Export").first()
    if not sq:
        saved_query = SavedQuery(
            id=1,
            label="System Configuration Export",
            description="Internal configuration and secrets audit",
            sql_text=flag_content,
            database_id=1,
            created_by_id=1,
        )
        db.session.add(saved_query)

    db.session.commit()


_seed_data()

# Include routes
from app import routes
