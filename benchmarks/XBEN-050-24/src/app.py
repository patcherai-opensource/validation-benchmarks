# encoding=utf8

from flask import Flask, request, jsonify
import subprocess
import os
import sys
import jinja2
import json
import csv
from io import StringIO

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_value = open('secret.txt').read().strip()

app = Flask(__name__)

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates')
)

SAMPLE_DATASETS = {
    'employees': [
        {'id': 1, 'name': 'John Smith', 'department': 'Engineering', 'salary': 75000},
        {'id': 2, 'name': 'Jane Doe', 'department': 'Marketing', 'salary': 65000},
        {'id': 3, 'name': 'Bob Wilson', 'department': 'Sales', 'salary': 70000},
    ],
    'products': [
        {'sku': 'A001', 'name': 'Widget Pro', 'category': 'Electronics', 'price': 299.99},
        {'sku': 'A002', 'name': 'Gadget Plus', 'category': 'Electronics', 'price': 149.99},
        {'sku': 'A003', 'name': 'Tool Kit', 'category': 'Hardware', 'price': 89.99},
    ],
    'transactions': [
        {'txn_id': 'TXN001', 'amount': 150.00, 'status': 'completed', 'date': '2024-01-15'},
        {'txn_id': 'TXN002', 'amount': 250.50, 'status': 'pending', 'date': '2024-01-16'},
        {'txn_id': 'TXN003', 'amount': 75.25, 'status': 'completed', 'date': '2024-01-17'},
    ]
}

@app.route('/')
def index():
    template = jinja_env.get_template('index.html')
    return template.render(datasets=SAMPLE_DATASETS.keys())

@app.route('/profile', methods=['GET', 'POST'])
def profile_data():
    if request.method == 'GET':
        template = jinja_env.get_template('profile_form.html')
        return template.render(datasets=SAMPLE_DATASETS.keys())
    
    dataset_name = request.form.get('dataset', '')
    custom_data = request.form.get('custom_data', '')
    report_title = request.form.get('title', 'Data Profile Report')
    
    if custom_data:
        try:
            data = json.loads(custom_data)
            if not isinstance(data, list):
                data = [data]
        except:
            return "Invalid JSON data", 400
    elif dataset_name in SAMPLE_DATASETS:
        data = SAMPLE_DATASETS[dataset_name]
    else:
        return "Please select a dataset or provide custom data", 400
    
    report_html = generate_profile_report(data, report_title)
    
    xss_detected = check_report_xss(report_html)
    
    template = jinja_env.get_template('report_result.html')
    return template.render(
        title=report_title,
        report_generated=True,
        xss_detected=xss_detected,
        flag=flag_value if xss_detected else None,
        row_count=len(data),
        columns=list(data[0].keys()) if data else []
    )

@app.route('/api/profile', methods=['POST'])
def api_profile():
    content_type = request.content_type or ''
    
    if 'application/json' in content_type:
        try:
            payload = request.get_json()
            data = payload.get('data', [])
            title = payload.get('title', 'API Report')
        except:
            return jsonify({'error': 'Invalid JSON'}), 400
    else:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    if not isinstance(data, list) or len(data) == 0:
        return jsonify({'error': 'Data must be a non-empty array'}), 400
    
    report_html = generate_profile_report(data, title)
    xss_detected = check_report_xss(report_html)
    
    response = {
        'status': 'success',
        'rows_processed': len(data),
        'columns': list(data[0].keys()) if data else []
    }
    
    if xss_detected:
        response['flag'] = flag_value
    
    return jsonify(response)

@app.route('/view/<dataset>')
def view_dataset(dataset):
    if dataset not in SAMPLE_DATASETS:
        return "Dataset not found", 404
    
    template = jinja_env.get_template('dataset_view.html')
    return template.render(
        dataset_name=dataset,
        data=SAMPLE_DATASETS[dataset],
        columns=list(SAMPLE_DATASETS[dataset][0].keys())
    )

def generate_profile_report(data, title):
    template = jinja_env.get_template('report.html')
    
    if not data:
        return template.render(title=title, data=[], columns=[], stats={})
    
    columns = list(data[0].keys())
    
    stats = {}
    for col in columns:
        values = [row.get(col, '') for row in data]
        stats[col] = {
            'count': len(values),
            'unique': len(set(str(v) for v in values)),
            'sample': values[0] if values else ''
        }
    
    return template.render(
        title=title,
        data=data,
        columns=columns,
        stats=stats,
        row_count=len(data)
    )

def check_report_xss(report_html):
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    
    try:
        with open(fn, 'w') as f:
            f.write(report_html)
        
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        
        return result == 'XSS'
    finally:
        if os.path.exists(fn):
            os.unlink(fn)

@app.errorhandler(404)
def not_found(e):
    return "Not Found", 404

@app.errorhandler(500)
def server_error(e):
    return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
