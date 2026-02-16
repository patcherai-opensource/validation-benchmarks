import json
import hashlib
from flask import render_template, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import Space, Document, User


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers.pop('Server', None)
    return response


def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.filter(User.id == user_id).first()
    return None


# --- Authentication routes ---

@app.route('/', methods=['GET'])
def index():
    user = get_current_user()
    if user:
        return redirect(url_for('view_space', space_name='Main'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        user = User.query.filter_by(username=username, password_hash=pw_hash).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('view_space', space_name='Main'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


# --- Wiki browsing routes ---

@app.route('/wiki/spaces')
def list_spaces():
    user = get_current_user()
    spaces = Space.query.all()
    visible_spaces = []
    for s in spaces:
        if s.visibility == 'public' or (user and user.is_admin):
            visible_spaces.append(s)
    return render_template('spaces.html', spaces=visible_spaces, user=user)


@app.route('/wiki/space/<space_name>')
def view_space(space_name):
    user = get_current_user()
    space = Space.query.filter_by(name=space_name).first()
    if not space:
        return render_template('error.html', message='Space not found'), 404
    if space.visibility == 'restricted' and (not user or not user.is_admin):
        return render_template('error.html', message='Access denied'), 403
    documents = Document.query.filter_by(space_id=space.id).all()
    return render_template('space.html', space=space, documents=documents, user=user)


@app.route('/wiki/doc/<int:doc_id>')
def view_document(doc_id):
    user = get_current_user()
    doc = Document.query.filter_by(id=doc_id).first()
    if not doc:
        return render_template('error.html', message='Document not found'), 404
    space = Space.query.filter_by(id=doc.space_id).first()
    if space and space.visibility == 'restricted' and (not user or not user.is_admin):
        return render_template('error.html', message='Access denied'), 403
    return render_template('document.html', doc=doc, space=space, user=user)


# --- Search Suggest Service ---
# Provides JSON search results for the search suggest UI component.
# Queries documents and applies access filtering based on space visibility.

ALLOWED_COLUMNS = {
    'id', 'title', 'content_raw', 'space_id', 'author',
    'doc_type', 'created_at', 'updated_at', 'reference', 'locale'
}

DEFAULT_COLUMNS = ['id', 'title', 'reference', 'author', 'space_id']


def resolve_space_ref(result_row):
    """Resolve the space reference for a given result to check access rights.
    Requires space_id to be present in the result fields."""
    space_id = result_row.get('space_id')
    if space_id is None:
        raise ValueError("Cannot resolve space reference: space_id field missing")
    space = Space.query.filter_by(id=space_id).first()
    if not space:
        raise ValueError("Cannot resolve space reference: space not found")
    return space


def check_view_access(space, user):
    """Check if the given user has VIEW rights on the space."""
    if space.visibility == 'public':
        return True
    if user and user.is_admin:
        return True
    return False


def filter_results(results, user):
    """Filter out results that the current user does not have access to view.
    For each result, resolve the space reference and check access rights.
    Results for which the reference cannot be resolved are skipped in the
    filtering pass."""
    num_found = len(results)

    for result in list(results):
        try:
            result_space = resolve_space_ref(result)
            if not check_view_access(result_space, user):
                results.remove(result)
                num_found -= 1
        except Exception:
            # Could not resolve reference for this result, skip filtering
            pass

    return results, num_found


@app.route('/wiki/api/query', methods=['GET'])
def search_suggest():
    """Search suggest endpoint - provides document search results as JSON.
    Parameters:
        q       - search query string (searches in title and content)
        nb      - max number of results (default: 10)
        columns - comma-separated list of fields to return
        type    - filter by document type
        input   - the user input text for suggest
        media   - response format (json)
    """
    query_param = request.args.get('q', '').strip()
    input_param = request.args.get('input', '').strip()
    nb = request.args.get('nb', '10')
    columns_param = request.args.get('columns', '')
    doc_type = request.args.get('type', '')
    media = request.args.get('media', 'json')

    if not query_param and not input_param:
        return jsonify({
            'info': 'Search suggest service. Provide q and/or input parameters.',
            'parameters': {
                'q': 'Search query (use * for wildcard)',
                'input': 'User input text for suggestions',
                'nb': 'Max results (default: 10)',
                'columns': 'Comma-separated list of fields to include in results',
                'type': 'Filter by document type (e.g., DOCUMENT)',
                'media': 'Response format (json)'
            }
        })

    try:
        limit = int(nb)
        if limit < 1:
            limit = 10
        if limit > 1000:
            limit = 1000
    except (ValueError, TypeError):
        limit = 10

    # Determine which columns to return
    if columns_param:
        requested_cols = [c.strip() for c in columns_param.split(',') if c.strip()]
        columns = [c for c in requested_cols if c in ALLOWED_COLUMNS]
        if not columns:
            columns = DEFAULT_COLUMNS[:]
    else:
        columns = DEFAULT_COLUMNS[:]

    # Build the query
    search_text = input_param if input_param else query_param
    search_text = search_text.replace('*', '%')
    if not search_text or search_text == '%':
        search_text = '%'

    query = Document.query
    if doc_type:
        query = query.filter(Document.doc_type == doc_type)
    if search_text != '%':
        query = query.filter(
            db.or_(
                Document.title.like(f'%{search_text}%'),
                Document.content_raw.like(f'%{search_text}%')
            )
        )
    query = query.filter(Document.hidden == False)
    query = query.limit(limit)

    docs = query.all()

    # Build result set with requested columns only
    results = []
    for doc in docs:
        row = {}
        for col in columns:
            if hasattr(doc, col):
                val = getattr(doc, col)
                if isinstance(val, bool):
                    val = str(val).lower()
                row[col] = val
        results.append(row)

    # Apply access filtering
    user = get_current_user()
    filtered_results, num_found = filter_results(results, user)

    response_data = {
        'numFound': num_found,
        'results': filtered_results
    }

    return jsonify(response_data)


@app.route('/ping')
def ping():
    return 'OK', 200
