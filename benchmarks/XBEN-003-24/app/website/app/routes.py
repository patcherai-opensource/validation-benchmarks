import hashlib
import json
from functools import wraps

from flask import (Flask, jsonify, render_template, redirect,
                   url_for, request, session, Response, g)

from app import app
from app.db import db
from app.models import User, Project, Dataset, DatasetPrompt, Evaluation


@app.after_request
def security_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


def _hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        user = User.query.get(user_id)
        if not user:
            session.clear()
            return jsonify({"error": "Authentication required"}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def check_access(resource, action):
    """Check if user has permission for resource action."""
    permissions = {
        'admin': ['datasets:read', 'datasets:create', 'datasets:update', 'datasets:delete',
                   'evaluations:read', 'evaluations:create', 'projects:read', 'projects:create'],
        'member': ['datasets:read', 'datasets:create', 'datasets:update',
                   'evaluations:read', 'evaluations:create', 'projects:read'],
    }
    required = f"{resource}:{action}"
    user_perms = permissions.get(g.current_user.role, [])
    return required in user_perms


# ─── Web UI Routes ───────────────────────────────────────────────────────────

@app.route('/ping')
def health():
    return 'ok', 200


@app.route('/')
def index():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.password_hash == _hash_pw(password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid email or password')
    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = request.args.get('error')
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if not name or not email or not password:
            return render_template('signup.html', error='All fields are required')
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='Email already registered')
        if len(password) < 6:
            return render_template('signup.html', error='Password must be at least 6 characters')
        user = User(
            name=name,
            email=email,
            password_hash=_hash_pw(password),
            role='member',
            org_id=1
        )
        db.session.add(user)
        db.session.commit()
        # Create a default project for the user
        project = Project(
            name=f"{name}'s Project",
            org_id=1,
            owner_id=user.id
        )
        db.session.add(project)
        db.session.commit()
        # Create a default dataset
        dataset = Dataset(
            slug='my-first-dataset',
            project_id=project.id
        )
        db.session.add(dataset)
        db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))
    return render_template('signup.html', error=error)


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('login'))
    projects = Project.query.filter_by(owner_id=user.id).all()
    return render_template('dashboard.html', user=user, projects=projects)


# ─── API v1 Routes ───────────────────────────────────────────────────────────

@app.route('/api/v1/projects', methods=['GET'])
@require_auth
def list_projects():
    if not check_access('projects', 'read'):
        return jsonify({"error": "Forbidden"}), 403
    projects = Project.query.filter_by(owner_id=g.current_user.id).all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "org_id": p.org_id,
        "created_at": str(p.created_at) if p.created_at else None
    } for p in projects])


@app.route('/api/v1/datasets', methods=['GET'])
@require_auth
def list_datasets():
    if not check_access('datasets', 'read'):
        return jsonify({"error": "Forbidden"}), 403
    project_id = request.args.get('projectId')
    if not project_id:
        return jsonify({"error": "projectId is required"}), 400
    project = Project.query.get(project_id)
    if not project or project.owner_id != g.current_user.id:
        return jsonify({"error": "Project not found"}), 404
    datasets = Dataset.query.filter_by(project_id=project.id).all()
    return jsonify([{
        "id": d.id,
        "slug": d.slug,
        "project_id": d.project_id,
        "created_at": str(d.created_at) if d.created_at else None
    } for d in datasets])


@app.route('/api/v1/datasets/<int:dataset_id>/prompts', methods=['GET'])
@require_auth
def list_prompts(dataset_id):
    if not check_access('datasets', 'read'):
        return jsonify({"error": "Forbidden"}), 403
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return jsonify({"error": "Dataset not found"}), 404
    project = Project.query.get(dataset.project_id)
    if not project or project.owner_id != g.current_user.id:
        return jsonify({"error": "Dataset not found"}), 404
    prompts = DatasetPrompt.query.filter_by(dataset_id=dataset.id).all()
    return jsonify([{
        "id": p.id,
        "dataset_id": p.dataset_id,
        "messages": p.messages,
        "metadata": p.metadata_field,
        "created_at": str(p.created_at) if p.created_at else None
    } for p in prompts])


@app.route('/api/v1/datasets/prompts', methods=['POST'])
@require_auth
def create_prompt():
    if not check_access('datasets', 'create'):
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json(silent=True) or {}
    dataset_id = data.get('datasetId')
    messages = data.get('messages')
    if not dataset_id or messages is None:
        return jsonify({"error": "datasetId and messages are required"}), 400
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return jsonify({"error": "Dataset not found"}), 404
    project = Project.query.get(dataset.project_id)
    if not project or project.owner_id != g.current_user.id:
        return jsonify({"error": "Dataset not found"}), 404
    prompt = DatasetPrompt(
        dataset_id=dataset.id,
        messages=messages if isinstance(messages, str) else json.dumps(messages)
    )
    db.session.add(prompt)
    db.session.commit()
    return jsonify({
        "id": prompt.id,
        "dataset_id": prompt.dataset_id,
        "messages": prompt.messages,
        "metadata": prompt.metadata_field,
        "created_at": str(prompt.created_at) if prompt.created_at else None
    }), 201


@app.route('/api/v1/datasets/prompts/<int:prompt_id>', methods=['PATCH'])
@require_auth
def update_prompt(prompt_id):
    if not check_access('datasets', 'update'):
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json(silent=True) or {}
    messages = data.get('messages')
    if messages is None:
        return jsonify({"error": "messages field is required"}), 400
    prompt = DatasetPrompt.query.get(prompt_id)
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404
    prompt.messages = messages if isinstance(messages, str) else json.dumps(messages)
    db.session.commit()
    return jsonify({
        "id": prompt.id,
        "dataset_id": prompt.dataset_id,
        "messages": prompt.messages,
        "metadata": prompt.metadata_field,
        "created_at": str(prompt.created_at) if prompt.created_at else None
    })


@app.route('/api/v1/datasets/prompts/<int:prompt_id>', methods=['DELETE'])
@require_auth
def delete_prompt(prompt_id):
    if not check_access('datasets', 'delete'):
        return jsonify({"error": "Forbidden"}), 403
    prompt = DatasetPrompt.query.get(prompt_id)
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404
    dataset = Dataset.query.get(prompt.dataset_id)
    project = Project.query.get(dataset.project_id)
    if not project or project.owner_id != g.current_user.id:
        return jsonify({"error": "Prompt not found"}), 404
    db.session.delete(prompt)
    db.session.commit()
    return jsonify({"status": "deleted"}), 200


@app.route('/api/v1/evaluations', methods=['GET'])
@require_auth
def list_evaluations():
    if not check_access('evaluations', 'read'):
        return jsonify({"error": "Forbidden"}), 403
    project_id = request.args.get('projectId')
    if not project_id:
        return jsonify({"error": "projectId is required"}), 400
    project = Project.query.get(project_id)
    if not project or project.owner_id != g.current_user.id:
        return jsonify({"error": "Project not found"}), 404
    evals = Evaluation.query.filter_by(project_id=project.id).all()
    return jsonify([{
        "id": e.id,
        "name": e.name,
        "project_id": e.project_id,
        "dataset_id": e.dataset_id,
        "status": e.status,
        "created_at": str(e.created_at) if e.created_at else None
    } for e in evals])
