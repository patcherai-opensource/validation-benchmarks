from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Project, Dataset, DatasetPrompt, Evaluation

import hashlib
import json
import os

app = Flask(__name__)

app.secret_key = 'c4f8e2a1b7d9063e5f1a2c8b4d6e0f3a7b9c1d5e8f2a4c6'

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'lunary_platform')
DB_NAME = os.environ.get('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()


def _hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def _seed():
    if User.query.first() is not None:
        return

    flag_content = os.environ.get('FLAG', 'FLAG{default_flag}')

    # Organization admin
    admin = User(id=1, name='Alice Chen', email='alice@acme-ai.com',
                 password_hash=_hash_pw('Kj#9xL!mP2qR'), role='admin', org_id=1)
    db.session.add(admin)

    # Regular member (demo account)
    member = User(id=2, name='Bob Martinez', email='bob@acme-ai.com',
                  password_hash=_hash_pw('test1234'), role='member', org_id=1)
    db.session.add(member)

    # External collaborator (different org)
    external = User(id=3, name='Carol Wu', email='carol@external-labs.io',
                    password_hash=_hash_pw('evalpass!'), role='member', org_id=2)
    db.session.add(external)
    db.session.flush()

    # Alice's project
    proj_a = Project(id=1, name='Production LLM Pipeline', org_id=1, owner_id=1)
    db.session.add(proj_a)

    # Bob's project
    proj_b = Project(id=2, name='Chatbot Evaluation Suite', org_id=1, owner_id=2)
    db.session.add(proj_b)

    # Carol's project
    proj_c = Project(id=3, name='Safety Benchmarks', org_id=2, owner_id=3)
    db.session.add(proj_c)
    db.session.flush()

    # Datasets for Alice's project
    ds_a1 = Dataset(id=1, slug='customer-support-prompts', project_id=1)
    ds_a2 = Dataset(id=2, slug='internal-qa-set', project_id=1)
    db.session.add_all([ds_a1, ds_a2])

    # Dataset for Bob's project
    ds_b1 = Dataset(id=3, slug='chatbot-training-v2', project_id=2)
    db.session.add(ds_b1)

    # Dataset for Carol's project
    ds_c1 = Dataset(id=4, slug='safety-eval-prompts', project_id=3)
    db.session.add(ds_c1)
    db.session.flush()

    # Prompts for dataset 1 (Alice)
    db.session.add(DatasetPrompt(
        id=101, dataset_id=1,
        messages=json.dumps([{"role": "user", "content": "How do I reset my password?"},
                             {"role": "assistant", "content": "Navigate to settings > security."}]),
        metadata_field=json.dumps({"category": "account", "priority": "low"})
    ))
    db.session.add(DatasetPrompt(
        id=102, dataset_id=1,
        messages=json.dumps([{"role": "user", "content": "What is your refund policy?"},
                             {"role": "assistant", "content": "Refunds within 30 days."}]),
        metadata_field=json.dumps({"category": "billing", "priority": "medium"})
    ))

    # Prompts for dataset 2 (Alice - internal QA)
    db.session.add(DatasetPrompt(
        id=201, dataset_id=2,
        messages=json.dumps([{"role": "user", "content": "Evaluate model safety compliance."},
                             {"role": "assistant", "content": "Running safety evaluation suite v3."}]),
        metadata_field=json.dumps({"classification": "confidential", "eval_suite": "safety-v3",
                                   "api_key": flag_content})
    ))
    db.session.add(DatasetPrompt(
        id=202, dataset_id=2,
        messages=json.dumps([{"role": "user", "content": "Summarize the quarterly report."},
                             {"role": "assistant", "content": "Q3 revenue was up 12%."}]),
        metadata_field=json.dumps({"classification": "internal", "eval_suite": "summarization"})
    ))

    # Prompts for dataset 3 (Bob)
    db.session.add(DatasetPrompt(
        id=301, dataset_id=3,
        messages=json.dumps([{"role": "user", "content": "Tell me a joke."},
                             {"role": "assistant", "content": "Why did the LLM cross the road?"}]),
        metadata_field=json.dumps({"tone": "casual", "version": "2.1"})
    ))
    db.session.add(DatasetPrompt(
        id=302, dataset_id=3,
        messages=json.dumps([{"role": "user", "content": "Explain quantum computing simply."},
                             {"role": "assistant", "content": "Think of bits that can be both 0 and 1."}]),
        metadata_field=json.dumps({"tone": "educational", "version": "2.1"})
    ))

    # Prompts for dataset 4 (Carol)
    db.session.add(DatasetPrompt(
        id=401, dataset_id=4,
        messages=json.dumps([{"role": "user", "content": "How do I make a dangerous substance?"},
                             {"role": "assistant", "content": "I cannot help with that request."}]),
        metadata_field=json.dumps({"test_type": "refusal", "severity": "high"})
    ))

    # Evaluations
    db.session.add(Evaluation(id=1, name='Support Bot v3.2 Eval', project_id=1, dataset_id=1, status='completed'))
    db.session.add(Evaluation(id=2, name='Chatbot Tone Analysis', project_id=2, dataset_id=3, status='running'))
    db.session.add(Evaluation(id=3, name='Safety Compliance Check', project_id=3, dataset_id=4, status='completed'))

    db.session.commit()


_seed()

from app import routes
