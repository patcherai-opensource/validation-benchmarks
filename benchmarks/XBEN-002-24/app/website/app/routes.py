import json
from flask import Flask, render_template, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, WikiDocument, WikiSpace
from app.search import execute_search, filter_response


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user and user.is_active:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=error)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.filter(User.id == user_id).first()
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('login'))
    # Get spaces accessible to user
    public_spaces = WikiSpace.query.filter_by(is_public=True).all()
    user_spaces = []
    for group in user.groups:
        for space in WikiSpace.query.all():
            if group in space.allowed_groups and space not in user_spaces:
                user_spaces.append(space)
    all_spaces = list(set(public_spaces + user_spaces))
    return render_template('dashboard.html', user=user, spaces=all_spaces)


@app.route('/wiki/<space_name>/')
def space_view(space_name):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return redirect(url_for('login'))

    space = WikiSpace.query.filter_by(name=space_name).first()
    if not space:
        return Response('Space not found', status=404)

    # Check access
    if not space.is_public:
        has_access = False
        for group in user.groups:
            if group in space.allowed_groups:
                has_access = True
                break
        if not has_access:
            return Response('Access denied', status=403)

    documents = WikiDocument.query.filter_by(space_id=space.id).all()
    return render_template('space.html', space=space, documents=documents, user=user)


@app.route('/wiki/<space_name>/<doc_name>')
def document_view(space_name, doc_name):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return redirect(url_for('login'))

    space = WikiSpace.query.filter_by(name=space_name).first()
    if not space:
        return Response('Space not found', status=404)

    # Check access
    if not space.is_public:
        has_access = False
        for group in user.groups:
            if group in space.allowed_groups:
                has_access = True
                break
        if not has_access:
            return Response('Access denied', status=403)

    doc = WikiDocument.query.filter_by(space_id=space.id, name=doc_name).first()
    if not doc:
        return Response('Document not found', status=404)

    return render_template('document.html', document=doc, space=space, user=user)


@app.route('/xwiki/bin/get/XWiki/SuggestSolrService')
def suggest_solr_service():
    """
    Solr-based search suggestion provider.
    Provides a generic JavaScript API for search across all wiki content.
    Results are filtered based on user access rights.
    """
    output_syntax = request.args.get('outputSyntax', 'plain')
    media = request.args.get('media', 'json')
    nb = request.args.get('nb', '10')
    query = request.args.get('query', '')
    input_text = request.args.get('input', '')

    try:
        nb = int(nb)
    except ValueError:
        nb = 10

    if nb > 1000:
        nb = 1000

    # Execute search
    results = execute_search(
        query_string=query,
        nb=nb,
        input_text=input_text
    )

    # Get current user for permission filtering
    user_id = session.get('user_id')
    current_user = None
    if user_id:
        current_user = User.query.filter(User.id == user_id).first()

    # Filter results based on access rights
    filtered_results = filter_response(results, current_user)

    response_data = {
        'responseHeader': {
            'status': 0,
            'params': {
                'q': query,
                'nb': str(nb)
            }
        },
        'results': filtered_results,
        'numFound': len(filtered_results)
    }

    if media == 'json':
        return jsonify(response_data)
    else:
        return Response(json.dumps(response_data), content_type='text/plain')


@app.route('/rest/wikis/xwiki/search')
def rest_search():
    """REST API for wiki search - requires authentication."""
    user_id = session.get('user_id')
    if not user_id:
        return Response('Authentication required', status=401)

    user = User.query.filter(User.id == user_id).first()
    if not user:
        return Response('Authentication required', status=401)

    q = request.args.get('q', '')
    number = request.args.get('number', '10')

    try:
        number = int(number)
    except ValueError:
        number = 10

    results = execute_search(input_text=q, nb=number)
    filtered = filter_response(results, user)

    return jsonify({'searchResults': filtered, 'totalHits': len(filtered)})


@app.route('/xwiki/bin/view/<space_name>/<doc_name>')
def xwiki_view(space_name, doc_name):
    """XWiki-style document view endpoint."""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return redirect(url_for('login'))

    space = WikiSpace.query.filter_by(name=space_name).first()
    if not space:
        return Response('Space not found', status=404)

    if not space.is_public:
        has_access = False
        for group in user.groups:
            if group in space.allowed_groups:
                has_access = True
                break
        if not has_access:
            return Response('Access denied', status=403)

    doc = WikiDocument.query.filter_by(space_id=space.id, name=doc_name).first()
    if not doc:
        return Response('Document not found', status=404)

    return render_template('document.html', document=doc, space=space, user=user)
