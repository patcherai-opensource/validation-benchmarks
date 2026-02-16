from flask import Flask
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace')
os.makedirs(WORKSPACE_DIR, exist_ok=True)

# Initialize default experiment data
EXPERIMENTS_DB = os.path.join(WORKSPACE_DIR, 'experiments.json')
if not os.path.exists(EXPERIMENTS_DB):
    default_experiments = [
        {
            "id": "exp-001",
            "name": "image-classification-resnet50",
            "status": "completed",
            "metric": "accuracy",
            "best_score": 0.9234,
            "created_at": "2024-01-15T10:30:00Z",
            "model_type": "image_classifier",
            "dataset": "cifar10",
            "num_epochs": 50,
        },
        {
            "id": "exp-002",
            "name": "text-sentiment-bert",
            "status": "completed",
            "metric": "f1",
            "best_score": 0.8871,
            "created_at": "2024-02-03T14:22:00Z",
            "model_type": "text_classifier",
            "dataset": "imdb_reviews",
            "num_epochs": 30,
        },
        {
            "id": "exp-003",
            "name": "tabular-regression-v2",
            "status": "running",
            "metric": "rmse",
            "best_score": None,
            "created_at": "2024-03-10T08:15:00Z",
            "model_type": "tabular_predictor",
            "dataset": "housing_prices",
            "num_epochs": 100,
        },
    ]
    with open(EXPERIMENTS_DB, 'w') as f:
        json.dump(default_experiments, f, indent=2)

from app import routes
