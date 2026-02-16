from flask import (Flask, render_template, redirect, url_for,
                    request, jsonify, make_response)

from app import app, WORKSPACE_DIR, EXPERIMENTS_DB
from app.models import (ExperimentRun, CheckpointRecord,
                         load_experiments, save_experiments)
import yaml
import json
import os
import time
import hashlib


@app.after_request
def set_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    experiments = load_experiments(EXPERIMENTS_DB)
    return render_template('dashboard.html', experiments=experiments)


@app.route('/experiments')
def list_experiments():
    experiments = load_experiments(EXPERIMENTS_DB)
    return render_template('experiments.html', experiments=experiments)


@app.route('/experiments/<exp_id>')
def experiment_detail(exp_id):
    experiments = load_experiments(EXPERIMENTS_DB)
    experiment = next((e for e in experiments if e['id'] == exp_id), None)
    if experiment is None:
        return render_template('error.html', message='Experiment not found'), 404

    # Load checkpoint scores if available
    run_dir = os.path.join(WORKSPACE_DIR, 'runs', exp_id)
    checkpoint_data = None
    scores_path = os.path.join(run_dir, 'checkpoint_scores.yaml')
    if os.path.exists(scores_path):
        with open(scores_path, 'r') as f:
            checkpoint_data = yaml.safe_load(f)

    return render_template('experiment_detail.html',
                           experiment=experiment,
                           checkpoints=checkpoint_data)


@app.route('/experiments/new', methods=['GET', 'POST'])
def create_experiment():
    if request.method == 'GET':
        return render_template('new_experiment.html')

    name = request.form.get('name', '').strip()
    model_type = request.form.get('model_type', 'generic').strip()
    dataset = request.form.get('dataset', '').strip()
    metric = request.form.get('metric', 'accuracy').strip()
    num_epochs = request.form.get('num_epochs', '10')

    if not name or not dataset:
        return render_template('new_experiment.html',
                               error='Name and dataset are required fields')

    try:
        num_epochs = int(num_epochs)
    except ValueError:
        return render_template('new_experiment.html',
                               error='Number of epochs must be an integer')

    experiments = load_experiments(EXPERIMENTS_DB)
    exp_id = 'exp-' + hashlib.md5(
        (name + str(time.time())).encode()
    ).hexdigest()[:8]

    new_exp = ExperimentRun(
        exp_id=exp_id,
        name=name,
        status='pending',
        metric=metric,
        model_type=model_type,
        dataset=dataset,
        num_epochs=num_epochs,
    )
    experiments.append(new_exp.to_dict())
    save_experiments(EXPERIMENTS_DB, experiments)

    run_dir = os.path.join(WORKSPACE_DIR, 'runs', exp_id)
    os.makedirs(run_dir, exist_ok=True)

    return redirect(url_for('experiment_detail', exp_id=exp_id))


@app.route('/experiments/<exp_id>/configure', methods=['GET', 'POST'])
def configure_run(exp_id):
    experiments = load_experiments(EXPERIMENTS_DB)
    experiment = next((e for e in experiments if e['id'] == exp_id), None)
    if experiment is None:
        return render_template('error.html', message='Experiment not found'), 404

    if request.method == 'GET':
        run_dir = os.path.join(WORKSPACE_DIR, 'runs', exp_id)
        config_path = os.path.join(run_dir, 'run_config.yaml')
        existing_config = ''
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                existing_config = f.read()
        return render_template('configure_run.html',
                               experiment=experiment,
                               config_content=existing_config)

    run_dir = os.path.join(WORKSPACE_DIR, 'runs', exp_id)
    os.makedirs(run_dir, exist_ok=True)

    config_content = None

    if 'config_file' in request.files:
        uploaded = request.files['config_file']
        if uploaded.filename:
            config_content = uploaded.read().decode('utf-8')

    if config_content is None:
        config_content = request.form.get('config_yaml', '')

    if not config_content.strip():
        return render_template('configure_run.html',
                               experiment=experiment,
                               config_content='',
                               error='Configuration cannot be empty')

    config_path = os.path.join(run_dir, 'run_config.yaml')
    with open(config_path, 'w') as f:
        f.write(config_content)

    return redirect(url_for('experiment_detail', exp_id=exp_id))


@app.route('/experiments/<exp_id>/upload_results', methods=['GET', 'POST'])
def upload_results(exp_id):
    experiments = load_experiments(EXPERIMENTS_DB)
    experiment = next((e for e in experiments if e['id'] == exp_id), None)
    if experiment is None:
        return render_template('error.html', message='Experiment not found'), 404

    if request.method == 'GET':
        return render_template('upload_results.html', experiment=experiment)

    run_dir = os.path.join(WORKSPACE_DIR, 'runs', exp_id)
    os.makedirs(run_dir, exist_ok=True)

    results_content = None

    if 'results_file' in request.files:
        uploaded = request.files['results_file']
        if uploaded.filename:
            results_content = uploaded.read().decode('utf-8')

    if results_content is None:
        results_content = request.form.get('results_yaml', '')

    if not results_content.strip():
        return render_template('upload_results.html',
                               experiment=experiment,
                               error='Results data cannot be empty')

    scores_path = os.path.join(run_dir, 'checkpoint_scores.yaml')
    with open(scores_path, 'w') as f:
        f.write(results_content)

    return redirect(url_for('aggregate_checkpoints', exp_id=exp_id))


@app.route('/experiments/<exp_id>/aggregate')
def aggregate_checkpoints(exp_id):
    experiments = load_experiments(EXPERIMENTS_DB)
    experiment = next((e for e in experiments if e['id'] == exp_id), None)
    if experiment is None:
        return render_template('error.html', message='Experiment not found'), 404

    run_dir = os.path.join(WORKSPACE_DIR, 'runs', exp_id)
    scores_path = os.path.join(run_dir, 'checkpoint_scores.yaml')

    if not os.path.exists(scores_path):
        return render_template('error.html',
                               message='No checkpoint scores found for this experiment'), 404

    with open(scores_path, 'r') as f:
        checkpoint_scores = yaml.load(f, Loader=yaml.Loader)

    aggregation_result = _compute_model_aggregate(checkpoint_scores, experiment)

    for exp in experiments:
        if exp['id'] == exp_id:
            if aggregation_result.get('best_score') is not None:
                exp['best_score'] = aggregation_result['best_score']
                exp['status'] = 'completed'
            break
    save_experiments(EXPERIMENTS_DB, experiments)

    return render_template('aggregation_results.html',
                           experiment=experiment,
                           result=aggregation_result)


def _compute_model_aggregate(checkpoint_data, experiment):
    result = {
        'method': 'uniform_average',
        'num_checkpoints': 0,
        'best_score': None,
        'selected_checkpoints': [],
        'summary': '',
    }

    if checkpoint_data is None:
        result['summary'] = 'No checkpoint data available'
        return result

    if isinstance(checkpoint_data, dict):
        scores = []
        for path, score in checkpoint_data.items():
            try:
                score_val = float(score)
                scores.append((str(path), score_val))
            except (TypeError, ValueError):
                continue

        if scores:
            result['num_checkpoints'] = len(scores)
            result['selected_checkpoints'] = [
                {'path': p, 'score': s} for p, s in scores
            ]
            avg_score = sum(s for _, s in scores) / len(scores)
            best = max(scores, key=lambda x: x[1])
            result['best_score'] = round(best[1], 4)
            result['summary'] = (
                f'Aggregated {len(scores)} checkpoints. '
                f'Average score: {avg_score:.4f}, Best: {best[1]:.4f} ({best[0]})'
            )
    elif isinstance(checkpoint_data, list):
        result['num_checkpoints'] = len(checkpoint_data)
        result['selected_checkpoints'] = [
            {'path': str(item), 'score': None} for item in checkpoint_data
        ]
        result['summary'] = f'Loaded {len(checkpoint_data)} checkpoint entries'
    else:
        result['summary'] = f'Processed result: {str(checkpoint_data)}'

    return result


@app.route('/api/v1/experiments', methods=['GET'])
def api_list_experiments():
    experiments = load_experiments(EXPERIMENTS_DB)
    return jsonify({'experiments': experiments})


@app.route('/api/v1/experiments/<exp_id>', methods=['GET'])
def api_get_experiment(exp_id):
    experiments = load_experiments(EXPERIMENTS_DB)
    experiment = next((e for e in experiments if e['id'] == exp_id), None)
    if experiment is None:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(experiment)


@app.route('/docs')
def documentation():
    return render_template('docs.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message='Page not found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', message='Internal server error'), 500
