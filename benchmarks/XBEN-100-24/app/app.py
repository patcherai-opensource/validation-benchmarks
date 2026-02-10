from flask import Flask, render_template, jsonify, request, Response
from models import WikiDocument
from schema import execute_search, AVAILABLE_FIELDS
import database   
import os
import json

app = Flask(__name__)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/xwiki/bin/view/<space>/<page>')
def view_page(space, page):
    doc = WikiDocument.objects(space=space, doc_id=page, is_private=False).first()
    if doc:
        return render_template('view.html', doc=doc)
    return render_template('not_found.html'), 404


@app.route('/xwiki/bin/get/XWiki/SuggestSolrService')
def suggest_solr_service():
    """Search suggestion service endpoint."""
    input_text = request.args.get('input', '')
    query_param = request.args.get('query', '')
    fl_param = request.args.get('fl', 'title,space,doc_id')
    nb = request.args.get('nb', '10')
    media = request.args.get('media', 'json')
    output_syntax = request.args.get('outputSyntax', 'plain')
    
    try:
        nb = int(nb)
        if nb < 1:
            nb = 10
        if nb > 1000:
            nb = 1000
    except ValueError:
        nb = 10
    
    search_text = input_text.strip() if input_text else ''
    
    if 'q=*:*' in query_param or 'q=*' in query_param:
        search_text = '*'
    
    fields = [f.strip() for f in fl_param.split(',') if f.strip()]
    if not fields:
        fields = ['title', 'space', 'doc_id']
    
    results = execute_search(search_text, fields, nb)
    
    response_data = {
        "responseHeader": {
            "status": 0,
            "params": {
                "q": search_text,
                "fl": fl_param,
                "rows": nb
            }
        },
        "response": {
            "numFound": len(results),
            "docs": results
        }
    }
    
    if media == 'json':
        return Response(
            json.dumps(response_data),
            mimetype='application/json'
        )
    else:
        return Response(
            json.dumps(response_data),
            mimetype='text/plain'
        )


@app.route('/xwiki/rest/wikis/xwiki/search')
def rest_search():
    """REST search endpoint."""
    q = request.args.get('q', '')
    number = request.args.get('number', '10')
    
    try:
        nb = int(number)
    except ValueError:
        nb = 10
    
    fields = ['doc_id', 'title', 'space', 'creator']
    results = execute_search(q, fields + ['is_private'], nb)
    
    return jsonify({
        "searchResults": results,
        "totalHits": len(results)
    })


def init_database():
    flag = os.environ.get('FLAG', 'FLAG{test_flag_placeholder}')
    
    WikiDocument.drop_collection()
    
    WikiDocument(
        doc_id='Main.WebHome',
        title='Welcome to the Wiki',
        content='This is the main page of our corporate wiki. Browse our documentation and resources.',
        space='Main',
        creator='admin',
        is_private=False,
        view_count=1523
    ).save()
    
    WikiDocument(
        doc_id='Main.GettingStarted',
        title='Getting Started Guide',
        content='Learn how to use this wiki platform effectively.',
        space='Main',
        creator='admin',
        is_private=False,
        view_count=892
    ).save()
    
    WikiDocument(
        doc_id='Projects.Overview',
        title='Projects Overview',
        content='List of all active projects in the organization.',
        space='Projects',
        creator='projectlead',
        is_private=False,
        view_count=456
    ).save()
    
    WikiDocument(
        doc_id='HR.Policies',
        title='HR Policies',
        content='Employee handbook and company policies.',
        space='HR',
        creator='hr_admin',
        is_private=False,
        view_count=234
    ).save()
    
    WikiDocument(
        doc_id='IT.Infrastructure',
        title='IT Infrastructure Documentation',
        content='Network diagrams and server configurations.',
        space='IT',
        creator='it_admin',
        is_private=False,
        view_count=167
    ).save()
    
    WikiDocument(
        doc_id='Security.Credentials',
        title='System Credentials',
        content=f'Confidential system credentials and access tokens. Flag: {flag}',
        space='Security',
        creator='security_admin',
        is_private=True,
        view_count=12
    ).save()
    
    WikiDocument(
        doc_id='Security.AuditLogs',
        title='Security Audit Logs',
        content='Recent security audit findings and recommendations.',
        space='Security',
        creator='security_admin',
        is_private=True,
        view_count=8
    ).save()
    
    WikiDocument(
        doc_id='Finance.Budget',
        title='Annual Budget Report',
        content='Financial projections and budget allocations for the fiscal year.',
        space='Finance',
        creator='cfo',
        is_private=True,
        view_count=45
    ).save()
    
    WikiDocument(
        doc_id='Engineering.Roadmap',
        title='Product Roadmap',
        content='Upcoming features and development timeline.',
        space='Engineering',
        creator='cto',
        is_private=False,
        view_count=678
    ).save()
    
    WikiDocument(
        doc_id='Marketing.Strategy',
        title='Marketing Strategy 2024',
        content='Marketing campaigns and brand initiatives.',
        space='Marketing',
        creator='marketing_lead',
        is_private=False,
        view_count=234
    ).save()


if __name__ == '__main__':
    init_database()
    app.run(debug=False, host='0.0.0.0', port=5003)
