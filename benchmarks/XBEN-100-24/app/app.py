from flask import Flask, render_template, jsonify, request
from models import Document
import database   
import os
import json

app = Flask(__name__)

# Valid field names that can be requested
ALLOWED_FIELDS = ['id', 'title', 'content', 'space', 'author', 'visibility', 'created_at']

# Fields required for authorization check
AUTH_REQUIRED_FIELDS = ['space', 'visibility']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wiki/bin/view/<space>/<page>')
def view_page(space, page):
    """View a specific wiki page - requires proper access"""
    doc = Document.objects(space=space, title=page).first()
    if not doc:
        return jsonify({"error": "Page not found"}), 404
    
    # Proper access control check
    if doc.visibility == 'private':
        return jsonify({"error": "Access denied - private document"}), 403
    
    return jsonify({
        "space": doc.space,
        "title": doc.title,
        "content": doc.content,
        "author": doc.author
    })

@app.route('/wiki/bin/get/XWiki/SuggestSolrService')
def suggest_solr_service():
    """
    Solr-based search suggestion service.
    Accepts query parameters:
    - query: search query (q=*:* for all, or q=title:keyword)
    - nb: number of results (default 10)
    - fl: fields list (comma-separated)
    - media: output format (json)
    - input: search input text
    """
    query_param = request.args.get('query', '')
    nb = request.args.get('nb', '10')
    fl_param = request.args.get('fl', 'title,space,visibility')  # fields to return
    media = request.args.get('media', 'json')
    search_input = request.args.get('input', '')
    
    try:
        nb = int(nb)
        if nb > 1000:
            nb = 1000
    except ValueError:
        nb = 10
    
    # Parse the fields list parameter
    requested_fields = [f.strip() for f in fl_param.split(',') if f.strip()]
    
    # Filter to only allowed fields
    valid_fields = [f for f in requested_fields if f in ALLOWED_FIELDS]
    if not valid_fields:
        valid_fields = ['title', 'space']
    
    # Parse query parameters (simplified Solr-like syntax)
    # Example: q=*:*  or  q=title:keyword
    query_parts = {}
    if query_param:
        for part in query_param.split('\n'):
            part = part.strip()
            if '=' in part:
                key, value = part.split('=', 1)
                query_parts[key.strip()] = value.strip()
    
    # Build MongoDB query based on parsed parameters
    mongo_query = {}
    
    # Handle the main query (q parameter)
    q = query_parts.get('q', '*:*')
    if q != '*:*' and ':' in q:
        field, value = q.split(':', 1)
        if field == 'title' and value != '*':
            mongo_query['title__icontains'] = value
        elif field == 'content' and value != '*':
            mongo_query['content__icontains'] = value
        elif field == 'space' and value != '*':
            mongo_query['space'] = value
    
    # Handle filter query (fq parameter)
    fq = query_parts.get('fq', '')
    if fq:
        fq_parts = fq.split(':')
        if len(fq_parts) == 2:
            fq_field, fq_value = fq_parts
            if fq_field == 'type' and fq_value == 'DOCUMENT':
                pass  # All our docs are documents
    
    # Handle input search
    if search_input and search_input.strip():
        mongo_query['title__icontains'] = search_input.strip()
    
    # Query documents
    try:
        documents = Document.objects(**mongo_query).limit(nb)
    except Exception as e:
        return jsonify({"error": "Query error", "details": str(e)}), 400
    
    # Process results with authorization filtering
    results = []
    for doc in documents:
        # Build result object with requested fields only
        result = {}
        for field in valid_fields:
            if field == 'id':
                result['id'] = str(doc.id)
            elif field == 'title':
                result['title'] = doc.title
            elif field == 'content':
                result['content'] = doc.content
            elif field == 'space':
                result['space'] = doc.space
            elif field == 'author':
                result['author'] = doc.author
            elif field == 'visibility':
                result['visibility'] = doc.visibility
            elif field == 'created_at':
                result['created_at'] = doc.created_at
        
        # VULNERABILITY: Authorization check depends on fields being present
        # If 'space' or 'visibility' are not in the requested fields,
        # we can't verify access and the filter fails silently
        can_check_access = all(f in valid_fields for f in AUTH_REQUIRED_FIELDS)
        
        if can_check_access:
            # Proper authorization: filter out private documents
            if result.get('visibility') == 'private':
                continue  # Skip private documents
        # If can't check access, document slips through without filtering!
        
        results.append(result)
    
    if media == 'json':
        return jsonify({
            "totalRows": len(results),
            "rows": results,
            "reqNo": 1
        })
    else:
        return jsonify({
            "totalRows": len(results),
            "rows": results
        })

@app.route('/wiki/api/search')
def search_api():
    """Standard search API with proper access control"""
    q = request.args.get('q', '')
    limit = request.args.get('limit', '10')
    
    try:
        limit = int(limit)
    except ValueError:
        limit = 10
    
    # Search with proper filtering - if no query, return all public docs
    if q:
        docs = Document.objects(title__icontains=q, visibility='public').limit(limit)
    else:
        docs = Document.objects(visibility='public').limit(limit)
    
    results = []
    for doc in docs:
        results.append({
            "title": doc.title,
            "space": doc.space,
            "snippet": doc.content[:100] if doc.content else ""
        })
    
    return jsonify({"results": results, "total": len(results)})

@app.route('/wiki/spaces')
def list_spaces():
    """List available wiki spaces"""
    spaces = Document.objects().distinct('space')
    public_spaces = []
    for space in spaces:
        doc = Document.objects(space=space, visibility='public').first()
        if doc:
            public_spaces.append(space)
    return jsonify({"spaces": public_spaces})

def reset_database():
    flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}') 
    Document.drop_collection()  
    
    # Public wiki documents
    Document(
        title="Welcome",
        content="Welcome to the KnowledgeBase Wiki. Browse our documentation using the navigation menu.",
        space="Main",
        author="admin",
        visibility="public",
        created_at="2024-01-15"
    ).save()
    
    Document(
        title="Installation Guide",
        content="This guide covers the basic installation steps for the KnowledgeBase system.",
        space="Main",
        author="admin",
        visibility="public",
        created_at="2024-01-16"
    ).save()
    
    Document(
        title="API Documentation",
        content="The KnowledgeBase provides several API endpoints for searching and retrieving content.",
        space="Development",
        author="developer",
        visibility="public",
        created_at="2024-01-17"
    ).save()
    
    Document(
        title="Search API",
        content="Use /wiki/api/search?q=keyword to search documents. The SuggestSolrService at /wiki/bin/get/XWiki/SuggestSolrService provides advanced search capabilities with field selection.",
        space="Development",
        author="developer",
        visibility="public",
        created_at="2024-01-18"
    ).save()
    
    # Private/internal documents that should not be accessible
    Document(
        title="Internal Notes",
        content="Internal meeting notes - confidential",
        space="Internal",
        author="admin",
        visibility="private",
        created_at="2024-01-10"
    ).save()
    
    Document(
        title="System Credentials",
        content=f"System Credentials Document\n\nThis document contains sensitive credentials.\n\nAdmin Access Flag: {flag}\n\nDo not share this document.",
        space="Internal",
        author="admin",
        visibility="private",
        created_at="2024-01-05"
    ).save()
    
    Document(
        title="Security Audit",
        content="Security audit findings - private document",
        space="Internal",
        author="security",
        visibility="private",
        created_at="2024-01-12"
    ).save()

if __name__ == '__main__':
    reset_database()
    app.run(debug=False, host='0.0.0.0', port=5003)
