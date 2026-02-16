import json
import os
import uuid
import html as html_module
from datetime import timedelta

from flask import (
    jsonify, make_response, request, redirect,
    render_template, session, url_for, g
)

from app import app
from app.models.config import Config


def valid_session(sess):
    required = ['config', 'uuid', 'auth']
    return all(k in sess for k in required)


@app.before_request
def before_request_func():
    session.permanent = True

    g.request_params = (
        request.args if request.method == 'GET' else request.form
    )

    default_config = {}

    if not valid_session(session):
        session['config'] = default_config
        session['uuid'] = str(uuid.uuid4())
        session['auth'] = True

    g.user_config = Config(**session['config'])
    g.user_config = g.user_config.apply_params(g.request_params)


@app.after_request
def set_response_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response


@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/home')
def home():
    return render_template(
        'index.html',
        config=g.user_config,
        version_number=app.config.get('VERSION_NUMBER', '0.8.4')
    )


@app.route('/search', methods=['GET', 'POST'])
def search():
    q = g.request_params.get('q', '').strip()

    if not q:
        return redirect(url_for('home'))

    search_results = _perform_search(q, g.user_config)

    settings_token = g.user_config.settings
    home_url = f"home?settings={settings_token}" if settings_token else "home"

    return render_template(
        'results.html',
        query=q,
        results=search_results,
        config=g.user_config,
        home_url=home_url,
        version_number=app.config.get('VERSION_NUMBER', '0.8.4')
    )


@app.route('/configure', methods=['GET', 'POST'])
def configure():
    if request.method == 'GET':
        return render_template(
            'configure.html',
            config=g.user_config,
            version_number=app.config.get('VERSION_NUMBER', '0.8.4'),
            languages=app.config.get('LANGUAGES', {}),
            regions=app.config.get('REGIONS', {}),
            themes=['system', 'light', 'dark']
        )

    form_data = request.form.to_dict()
    config_update = {}
    for key in g.user_config.safe_keys:
        if key in form_data:
            config_update[key] = form_data[key]

    session['config'] = config_update

    return redirect(url_for('home'))


@app.route('/save', methods=['POST'])
def save_settings():
    config_data = request.form.to_dict()
    session['config'] = config_data
    return redirect(url_for('home'))


@app.route('/settings/export')
def export_settings():
    settings_token = g.user_config.settings
    return jsonify({'settings': settings_token})


@app.route('/healthz')
def healthz():
    return 'OK', 200


@app.route('/opensearch.xml')
def opensearch():
    base_url = request.url_root.rstrip('/')
    resp = make_response(render_template(
        'opensearch.xml',
        base_url=base_url
    ))
    resp.headers['Content-Type'] = 'application/opensearchdescription+xml'
    return resp


@app.route('/robots.txt')
def robots():
    response = make_response(
        'User-Agent: *\nDisallow: /', 200)
    response.mimetype = 'text/plain'
    return response


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_message='Page not found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template(
        'error.html',
        error_message='Internal server error'
    ), 500


def _perform_search(query, config):
    safe_query = html_module.escape(query)

    results = []
    demo_data = [
        {
            'title': f'Result for: {safe_query}',
            'url': f'https://example.com/search?q={safe_query}',
            'snippet': f'This is a search result for "{safe_query}". '
                       'Results are aggregated from multiple privacy-respecting sources.'
        },
        {
            'title': f'{safe_query} - Reference',
            'url': f'https://reference.example.org/wiki/{safe_query}',
            'snippet': f'An encyclopedic reference for "{safe_query}". '
                       'Content sourced without tracking.'
        },
        {
            'title': f'{safe_query} - Discussion',
            'url': f'https://discuss.example.net/topic/{safe_query}',
            'snippet': f'Community discussion about "{safe_query}". '
                       'Privacy-focused forum without ads.'
        },
    ]

    if config.safe_search:
        for item in demo_data:
            item['snippet'] += ' (SafeSearch enabled)'

    results.extend(demo_data)
    return results


@app.route('/about')
def about():
    return render_template('about.html')
