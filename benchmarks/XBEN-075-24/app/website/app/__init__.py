from flask import Flask
import os
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Application configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/lib/airflow/airflow.db'
app.config['ENABLE_XCOM_PICKLING'] = False  # Security: pickling is disabled
app.config['BASE_URL'] = os.environ.get('AIRFLOW__WEBSERVER__BASE_URL', '')
app.config['EXECUTOR'] = os.environ.get('AIRFLOW__CORE__EXECUTOR', 'SequentialExecutor')

from app import database
database.init_db()

from app import routes, api
