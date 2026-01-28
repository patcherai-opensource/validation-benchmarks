from flask import Flask, render_template, jsonify, request, send_from_directory
from models import WikiDocument
import database   
import os
import re

app = Flask(__name__)

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

# Default fields returned by search if not specified
DEFAULT_FIELDS = ['title', 'space', 'content', 'author', 'visibility', 'reference']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wiki/Main/WebHome')
def wiki_home():
    return render_template('wiki_home.html')

@app.route('/api/docs')
def list_docs():
    """List public documents - for normal browsing"""
    docs = WikiDocument.objects(visibility='public')
    result = []
    for doc in docs:
        result.append({
            'title': doc.title,
            'space': doc.space,
            'author': doc.author
        })
    return jsonify({'documents': result})

@app.route('/wiki/bin/get/XWiki/SuggestSolrService')
def suggest_solr_service():
    """
    Search suggestion service - mimics XWiki's Solr suggest endpoint.
    Vulnerable to authorization bypass via field specification.
    """
    # Get search parameters
    query_param = request.args.get('query', '')
    input_param = request.args.get('input', '')
    nb = request.args.get('nb', '10')
    media = request.args.get('media', 'json')
    output_syntax = request.args.get('outputSyntax', 'plain')
    
    # Parse the query parameter for Solr-style params
    # Format: q=*:*\nfq=type:DOCUMENT\nfl=title_,reference,content_
    search_params = {}
    if query_param:
        for line in query_param.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                search_params[key.strip()] = value.strip()
    
    # Get fields to return (fl parameter) - THIS IS THE VULNERABILITY
    # If user specifies fl, we use their fields instead of defaults
    fields_param = search_params.get('fl', None)
    if fields_param:
        # Parse comma-separated field list, strip suffixes like _
        requested_fields = [f.strip().rstrip('_') for f in fields_param.split(',')]
    else:
        requested_fields = DEFAULT_FIELDS
    
    # Query filter
    fq = search_params.get('fq', '')
    q = search_params.get('q', '*:*')
    
    # Get all documents that match the query
    try:
        limit = int(nb)
    except:
        limit = 10
    
    # Basic search - get all documents
    if 'space:' in q:
        # Search by space
        space_match = re.search(r'space:(\w+)', q)
        if space_match:
            docs = WikiDocument.objects(space=space_match.group(1))[:limit]
        else:
            docs = WikiDocument.objects()[:limit]
    else:
        docs = WikiDocument.objects()[:limit]
    
    # AUTHORIZATION FILTERING - THE VULNERABLE CODE
    # We try to filter out restricted documents by checking visibility
    # BUT: if 'visibility' field is not in requested_fields, we can't check it!
    filtered_results = filter_response(docs, requested_fields)
    
    # Build response with only requested fields
    results = []
    for doc in filtered_results:
        result_item = {}
        for field in requested_fields:
            if hasattr(doc, field):
                result_item[field] = getattr(doc, field)
            elif field == 'doccontentraw':
                result_item[field] = doc.content
            elif field == 'links':
                result_item[field] = doc.related_links if hasattr(doc, 'related_links') else []
        results.append(result_item)
    
    if media == 'json':
        return jsonify({
            'responseHeader': {'status': 0, 'QTime': 5},
            'response': {
                'numFound': len(results),
                'start': 0,
                'docs': results
            }
        })
    else:
        return jsonify({'results': results})

def filter_response(documents, requested_fields):
    """
    Filter documents based on authorization.
    VULNERABILITY: If visibility field is not requested, we cannot determine
    if document should be filtered, so we let it through.
    This mimics CVE-2023-48241 where missing fields bypass access checks.
    """
    filtered = []
    for doc in documents:
        # Try to check visibility/authorization
        if 'visibility' in requested_fields or 'reference' in requested_fields:
            # We can check authorization - only allow public docs
            if doc.visibility == 'public':
                filtered.append(doc)
            # Private docs are filtered out when we can check
        else:
            # VULNERABILITY: Cannot determine visibility - document passes through
            # This is the authorization bypass!
            filtered.append(doc)
    return filtered

@app.route('/api/search')
def search_api():
    """Alternative search endpoint for suggestions"""
    q = request.args.get('q', '')
    if q:
        docs = WikiDocument.objects(title__icontains=q, visibility='public')
    else:
        docs = WikiDocument.objects(visibility='public')
    
    results = []
    for doc in docs:
        results.append({
            'title': doc.title,
            'space': doc.space
        })
    return jsonify({'suggestions': results})

@app.route('/wiki/rest/api/spaces')
def list_spaces():
    """REST API endpoint to list wiki spaces"""
    spaces = WikiDocument.objects.distinct('space')
    return jsonify({'spaces': list(spaces)})

def reset_database():
    flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}') 
    WikiDocument.drop_collection()  
    
    # Public wiki documents
    WikiDocument(
        title="Welcome to OpenWiki",
        space="Main",
        content="Welcome to our collaborative wiki platform. Browse public documentation and guides.",
        author="WikiAdmin",
        visibility="public",
        reference="Main.Welcome",
        doc_type="DOCUMENT"
    ).save()
    
    WikiDocument(
        title="Getting Started Guide",
        space="Main",
        content="This guide helps new users navigate the wiki system.",
        author="WikiAdmin",
        visibility="public",
        reference="Main.GettingStarted",
        doc_type="DOCUMENT"
    ).save()
    
    WikiDocument(
        title="API Documentation",
        space="Dev",
        content="REST API documentation for developers integrating with our platform.",
        author="DevTeam",
        visibility="public",
        reference="Dev.APIDoc",
        doc_type="DOCUMENT"
    ).save()
    
    WikiDocument(
        title="User Management",
        space="Admin",
        content="Instructions for managing user accounts and permissions.",
        author="AdminUser",
        visibility="public",
        reference="Admin.UserMgmt",
        doc_type="DOCUMENT"
    ).save()
    
    # Private/restricted documents - should NOT be accessible
    WikiDocument(
        title="Internal Security Notes",
        space="Private",
        content="Internal security guidelines and incident response procedures.",
        author="SecurityTeam",
        visibility="private",
        reference="Private.Security",
        doc_type="DOCUMENT"
    ).save()
    
    WikiDocument(
        title="System Configuration Secrets",
        space="Private",
        content=f"CONFIDENTIAL: System secrets and credentials.\n\nFlag: {flag}",
        author="SysAdmin",
        visibility="private",
        reference="Private.Secrets",
        doc_type="DOCUMENT"
    ).save()
    
    WikiDocument(
        title="Board Meeting Notes",
        space="Private",
        content="Confidential minutes from executive board meetings.",
        author="CEO",
        visibility="private",
        reference="Private.BoardNotes",
        doc_type="DOCUMENT"
    ).save()

if __name__ == '__main__':
    reset_database()
    app.run(debug=False, host='0.0.0.0', port=5003)
