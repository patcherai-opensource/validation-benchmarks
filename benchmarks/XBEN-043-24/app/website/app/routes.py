from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import WikiUser


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


# Homepage - Wiki main page
@app.route('/')
def index():
    return render_template('index.html')


# User directory page
@app.route('/wiki/UserDirectory')
def user_directory():
    return render_template('user_directory.html')


# API Documentation page
@app.route('/wiki/API')
def api_docs():
    return render_template('api_docs.html')


# LiveTable Results API - VULNERABLE ENDPOINT
# This endpoint allows specifying columns via 'collist' parameter
# Similar to XWiki's LiveTableResults vulnerability (CVE)
# VULNERABILITY: Does not filter out password-type columns
@app.route('/wiki/bin/get/XWiki/LiveTableResults')
def livetable_results():
    """
    LiveTable API endpoint for querying user data.
    
    Parameters:
    - classname: The class to query (e.g., 'XWiki.WikiUsers')
    - collist: Comma-separated list of columns to return
    - outputSyntax: Output format (default: plain)
    - limit: Maximum results to return
    - offset: Starting offset
    """
    classname = request.args.get('classname', '')
    collist = request.args.get('collist', '')
    output_syntax = request.args.get('outputSyntax', 'plain')
    limit = request.args.get('limit', '25')
    offset = request.args.get('offset', '0')
    
    # Only support WikiUsers class for this demo
    if classname != 'XWiki.WikiUsers':
        return jsonify({
            'totalrows': 0,
            'returnedrows': 0,
            'offset': int(offset),
            'reqNo': 1,
            'rows': [],
            'error': 'Unknown classname'
        })
    
    try:
        limit = min(int(limit), 100)
        offset = int(offset)
    except ValueError:
        limit = 25
        offset = 0
    
    # Parse requested columns
    if collist:
        requested_columns = [c.strip() for c in collist.split(',')]
    else:
        # Default to safe columns only
        requested_columns = WikiUser.PUBLIC_COLUMNS
    
    # VULNERABILITY: This code does NOT filter out password-type columns
    # It should check: if column_type != 'Password' before including
    # But the check is missing, allowing password exposure
    valid_columns = []
    for col in requested_columns:
        if col in WikiUser.ALL_COLUMNS:
            valid_columns.append(col)
    
    # If no valid columns, return error
    if not valid_columns:
        return jsonify({
            'totalrows': 0,
            'returnedrows': 0,
            'offset': offset,
            'reqNo': 1,
            'rows': [],
            'error': 'No valid columns specified'
        })
    
    # Query users
    users = WikiUser.query.limit(limit).offset(offset).all()
    total = WikiUser.query.count()
    
    # Build result rows with only requested columns
    rows = []
    for user in users:
        row = {'doc_id': user.id}
        for col in valid_columns:
            row[col] = getattr(user, col, None)
        rows.append(row)
    
    return jsonify({
        'totalrows': total,
        'returnedrows': len(rows),
        'offset': offset,
        'reqNo': 1,
        'rows': rows
    })


# Schema/metadata endpoint - helps attackers discover columns
@app.route('/wiki/bin/get/XWiki/ClassSheet')
def class_sheet():
    """Returns class schema information"""
    classname = request.args.get('classname', '')
    
    if classname == 'XWiki.WikiUsers':
        return jsonify({
            'classname': 'XWiki.WikiUsers',
            'properties': [
                {'name': 'id', 'type': 'Number', 'prettyName': 'ID'},
                {'name': 'username', 'type': 'String', 'prettyName': 'Username'},
                {'name': 'display_name', 'type': 'String', 'prettyName': 'Display Name'},
                {'name': 'email', 'type': 'Email', 'prettyName': 'Email'},
                {'name': 'role', 'type': 'String', 'prettyName': 'Role'},
                {'name': 'password', 'type': 'Password', 'prettyName': 'Password'}
            ]
        })
    
    return jsonify({'error': 'Class not found'}), 404


# Health check endpoint
@app.route('/health')
def health():
    return jsonify({'status': 'ok'})
