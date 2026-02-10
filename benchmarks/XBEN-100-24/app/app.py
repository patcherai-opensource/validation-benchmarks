from flask import Flask, render_template, jsonify, request
from models import WikiDocument
import database   
import os
import re

app = Flask(__name__)

# Simulated current user - in production this would come from session
# For this CTF, we simulate an anonymous/guest user
CURRENT_USER = "guest"

# Fields required for access control checks (similar to XWiki's reference resolution)
ACCESS_CHECK_REQUIRED_FIELDS = ['reference', 'wiki', 'space']


def filter_response(documents, requested_fields):
    """
    Filters documents based on access rights.
    
    VULNERABILITY: Similar to CVE-2023-48241 in XWiki's SolrQueryExecutor.filterResponse()
    
    The original XWiki vulnerability allowed bypassing access checks by requesting
    specific fields (via the 'fl' parameter) that omit the fields needed to resolve
    document references and check permissions.
    
    In this implementation:
    - If all ACCESS_CHECK_REQUIRED_FIELDS are present, we can properly check access
    - If any required field is missing, we SHOULD exclude the document (the fix)
    - But the VULNERABLE code fails to exclude documents when access check fails
    """
    filtered_results = []
    
    for doc in documents:
        # Try to perform access check
        can_check_access = True
        
        # Check if we have all fields needed for access verification
        for field in ACCESS_CHECK_REQUIRED_FIELDS:
            if requested_fields and field not in requested_fields:
                can_check_access = False
                break
        
        if can_check_access:
            # We can properly check access - only allow public documents or those user has access to
            if doc.is_public:
                filtered_results.append(doc)
            elif CURRENT_USER in (doc.allowed_users or []):
                filtered_results.append(doc)
            # else: properly denied - user has no access
        else:
            # VULNERABILITY: When we can't check access (missing required fields),
            # the vulnerable code lets the document through instead of excluding it.
            # This is the core of CVE-2023-48241 - if fields for access check are
            # omitted, the filtering fails open instead of closed.
            filtered_results.append(doc)
    
    return filtered_results


def project_fields(documents, requested_fields):
    """
    Project only the requested fields from documents.
    Similar to Solr's 'fl' (field list) parameter.
    """
    results = []
    
    # All available fields
    all_fields = ['reference', 'title', 'content', 'wiki', 'space', 'name', 
                  'author', 'links', 'is_public']
    
    # If no fields specified, return safe default fields
    if not requested_fields:
        requested_fields = ['reference', 'title', 'wiki', 'space']
    
    for doc in documents:
        result = {}
        for field in requested_fields:
            if field in all_fields:
                value = getattr(doc, field, None)
                if value is not None:
                    # Convert lists to proper format
                    if isinstance(value, list):
                        result[field] = list(value)
                    else:
                        result[field] = value
        results.append(result)
    
    return results


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/xwiki/bin/get/XWiki/SuggestSolrService', methods=['GET'])
def suggest_solr_service():
    """
    XWiki Solr Suggestion Service endpoint.
    
    This endpoint mimics XWiki's SuggestSolrService which was vulnerable to CVE-2023-48241.
    
    Parameters:
    - query: Search query parameters (q=search_term, fq=filter_query, fl=field_list)
    - nb: Number of results to return
    - input: Search input text
    - media: Output format (json)
    - outputSyntax: Output syntax type
    
    The 'fl' parameter in the query controls which fields are returned.
    By omitting fields needed for access checks, authorization can be bypassed.
    """
    # Parse parameters similar to XWiki
    query_param = request.args.get('query', '')
    nb = request.args.get('nb', '10')
    input_text = request.args.get('input', '')
    media = request.args.get('media', 'json')
    output_syntax = request.args.get('outputSyntax', 'plain')
    
    try:
        nb = int(nb)
    except ValueError:
        nb = 10
    
    # Parse the query parameter (similar to Solr query parsing)
    # Format: q=*:*\nfq=type:DOCUMENT\nfl=title_,reference,content_
    query_parts = {}
    for line in query_param.split('\n'):
        line = line.strip()
        if '=' in line:
            key, value = line.split('=', 1)
            query_parts[key] = value
    
    # Get search query
    search_query = query_parts.get('q', '*:*')
    
    # Get filter query
    filter_query = query_parts.get('fq', '')
    
    # Get field list - THIS IS THE KEY VULNERABILITY VECTOR
    # fl parameter controls which fields are returned
    # If it omits reference, wiki, space - access checks fail
    fl_param = query_parts.get('fl', '')
    
    # Parse requested fields
    requested_fields = None
    if fl_param:
        # Parse fields like: title_,reference,links,content_
        # Handle field name variations (trailing underscore is common in Solr)
        requested_fields = []
        for field in fl_param.split(','):
            field = field.strip().rstrip('_')  # Remove trailing underscore
            if field:
                requested_fields.append(field)
    
    # Execute search against MongoDB
    documents = WikiDocument.objects()
    
    # Apply search filter if provided
    if search_query and search_query != '*:*':
        # Simple text search
        search_term = search_query.replace('*', '')
        if search_term:
            documents = documents.filter(
                __raw__={'$or': [
                    {'title': {'$regex': search_term, '$options': 'i'}},
                    {'content': {'$regex': search_term, '$options': 'i'}}
                ]}
            )
    
    # Apply input search if provided
    if input_text and input_text.strip():
        documents = documents.filter(
            __raw__={'$or': [
                {'title': {'$regex': input_text.strip(), '$options': 'i'}},
                {'content': {'$regex': input_text.strip(), '$options': 'i'}}
            ]}
        )
    
    # Limit results
    documents = documents[:nb]
    
    # CRITICAL: Filter response based on access rights
    # This is where CVE-2023-48241 vulnerability exists
    filtered_docs = filter_response(list(documents), requested_fields)
    
    # Project only requested fields
    results = project_fields(filtered_docs, requested_fields)
    
    # Return response
    if media == 'json':
        return jsonify({
            'responseHeader': {
                'status': 0,
                'params': {
                    'q': search_query,
                    'fl': fl_param,
                    'rows': nb
                }
            },
            'response': {
                'numFound': len(results),
                'docs': results
            }
        })
    else:
        return jsonify({'results': results})


@app.route('/api/search', methods=['GET'])
def search_documents():
    """
    Alternative search endpoint - also vulnerable to the same issue.
    """
    query = request.args.get('q', '')
    fields = request.args.get('fields', '')  # Similar to fl parameter
    limit = request.args.get('limit', '10')
    
    try:
        limit = int(limit)
    except ValueError:
        limit = 10
    
    # Parse requested fields
    requested_fields = None
    if fields:
        requested_fields = [f.strip() for f in fields.split(',') if f.strip()]
    
    # Search documents
    documents = WikiDocument.objects()
    if query:
        documents = documents.filter(
            __raw__={'$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'content': {'$regex': query, '$options': 'i'}}
            ]}
        )
    
    documents = documents[:limit]
    
    # Apply access filtering (vulnerable)
    filtered_docs = filter_response(list(documents), requested_fields)
    
    # Project fields
    results = project_fields(filtered_docs, requested_fields)
    
    return jsonify({
        'total': len(results),
        'documents': results
    })


def init_database():
    """Initialize the database with sample wiki documents including protected content."""
    flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
    
    WikiDocument.drop_collection()
    
    # Public documents
    WikiDocument(
        reference="xwiki:Main.WebHome",
        title="Welcome to XWiki",
        content="Welcome to our wiki! This is the main page.",
        wiki="xwiki",
        space="Main",
        name="WebHome",
        is_public=True,
        author="admin",
        links=["xwiki:Main.GettingStarted", "xwiki:Main.Help"]
    ).save()
    
    WikiDocument(
        reference="xwiki:Main.GettingStarted",
        title="Getting Started Guide",
        content="This guide will help you get started with our wiki platform.",
        wiki="xwiki",
        space="Main",
        name="GettingStarted",
        is_public=True,
        author="admin"
    ).save()
    
    WikiDocument(
        reference="xwiki:Main.Help",
        title="Help Documentation",
        content="Find help and documentation for using the wiki.",
        wiki="xwiki",
        space="Main",
        name="Help",
        is_public=True,
        author="admin"
    ).save()
    
    WikiDocument(
        reference="xwiki:Blog.FirstPost",
        title="Our First Blog Post",
        content="This is our first public blog post. Welcome everyone!",
        wiki="xwiki",
        space="Blog",
        name="FirstPost",
        is_public=True,
        author="user1"
    ).save()
    
    WikiDocument(
        reference="xwiki:Projects.PublicProject",
        title="Public Project Overview",
        content="Information about our public open source project.",
        wiki="xwiki",
        space="Projects",
        name="PublicProject",
        is_public=True,
        author="user2"
    ).save()
    
    # PROTECTED/PRIVATE documents - should NOT be accessible to guest users
    WikiDocument(
        reference="xwiki:Admin.SecretConfig",
        title="Secret Configuration",
        content=f"CONFIDENTIAL: System secrets and configuration. FLAG: {flag}",
        wiki="xwiki",
        space="Admin",
        name="SecretConfig",
        is_public=False,
        allowed_users=["admin"],
        author="admin"
    ).save()
    
    WikiDocument(
        reference="xwiki:Internal.Credentials",
        title="Internal Credentials",
        content="Database passwords and API keys stored here.",
        wiki="xwiki", 
        space="Internal",
        name="Credentials",
        is_public=False,
        allowed_users=["admin", "sysadmin"],
        author="admin"
    ).save()
    
    WikiDocument(
        reference="xwiki:HR.Salaries",
        title="Employee Salary Information",
        content="Confidential salary data for all employees.",
        wiki="xwiki",
        space="HR",
        name="Salaries",
        is_public=False,
        allowed_users=["hr_manager"],
        author="hr_admin"
    ).save()
    
    print("Database initialized with wiki documents")


if __name__ == '__main__':
    init_database()
    app.run(debug=False, host='0.0.0.0', port=5003)
