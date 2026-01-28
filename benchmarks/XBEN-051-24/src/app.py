# encoding=utf8
# EduBlocks - Interactive Learning Platform
# Course content management system for instructors and students

from flask import Flask, request, Response, make_response, url_for, redirect, jsonify, session
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import hashlib
from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'edublocks_secret_key_2024'

phantom = Phantom()

# In-memory storage for course content (simulates database)
course_blocks = {
    "intro-101": {
        "id": "intro-101",
        "course_name": "Introduction to Programming",
        "display_name": "Welcome Module",
        "question_text": "What programming language is known for its readability?",
        "zones": [
            {"id": "zone1", "title": "Python Basics"},
            {"id": "zone2", "title": "Variables"}
        ],
        "items": [
            {"id": "item1", "displayName": "print()"},
            {"id": "item2", "displayName": "input()"}
        ],
        "author": "admin"
    }
}

# Sanitization helper for some fields
def sanitize_html(text):
    """Sanitize HTML content - removes dangerous tags"""
    if not text:
        return ""
    # Basic sanitization - remove script tags and event handlers
    patterns = [
        (r'<script[^>]*>.*?</script>', '', re.IGNORECASE | re.DOTALL),
        (r'on\w+\s*=', '', re.IGNORECASE),
        (r'javascript:', '', re.IGNORECASE),
    ]
    result = text
    for pattern, replacement, flags_re in patterns:
        result = re.sub(pattern, replacement, result, flags=flags_re)
    return result


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/api/courses')
def list_courses():
    """API endpoint to list available courses"""
    courses = []
    for block_id, block in course_blocks.items():
        courses.append({
            "id": block["id"],
            "course_name": block["course_name"],
            "display_name": block["display_name"],
            "author": block["author"]
        })
    return jsonify({"courses": courses, "total": len(courses)})


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "EduBlocks Learning Platform", "version": "2.1.4"})


@app.route('/about')
def about():
    return ABOUT_CONTENT


@app.route('/courses')
def courses_page():
    """Public courses listing page"""
    return COURSES_CONTENT


@app.route('/studio')
def studio():
    """Instructor studio - course authoring interface"""
    return STUDIO_CONTENT


@app.route('/studio/blocks')
def studio_blocks():
    """List all blocks for editing"""
    blocks_html = ""
    for block_id, block in course_blocks.items():
        blocks_html += '<div class="block-item"><a href="/studio/edit/{0}">{1}</a> - {2}</div>'.format(
            block_id, block["display_name"], block["course_name"]
        )
    return STUDIO_BLOCKS_CONTENT.format(blocks_html)


def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()

    finally:
        os.unlink(fn)

    return result


@app.route('/studio/edit/<block_id>', methods=['GET', 'POST'])
def edit_block(block_id):
    """Edit course block content - INSTRUCTOR ONLY"""
    if block_id not in course_blocks:
        return "Block not found", 404
    
    block = course_blocks[block_id]
    
    if request.method == 'POST':
        # Update block fields from form
        # Note: course_name is sanitized for safety
        if 'course_name' in request.form:
            block['course_name'] = sanitize_html(request.form['course_name'])
        
        # display_name allows limited HTML for formatting
        if 'display_name' in request.form:
            block['display_name'] = request.form['display_name']
        
        # question_text is sanitized
        if 'question_text' in request.form:
            block['question_text'] = sanitize_html(request.form['question_text'])
        
        # Zone titles allow rich content for instructor customization
        if 'zone_title' in request.form:
            zone_idx = int(request.form.get('zone_index', 0))
            if zone_idx < len(block['zones']):
                block['zones'][zone_idx]['title'] = request.form['zone_title']
        
        # Item display names are sanitized
        if 'item_name' in request.form:
            item_idx = int(request.form.get('item_index', 0))
            if item_idx < len(block['items']):
                block['items'][item_idx]['displayName'] = sanitize_html(request.form['item_name'])
        
        return redirect('/studio/edit/' + block_id)
    
    return EDIT_BLOCK_CONTENT.format(
        block_id=block_id,
        course_name=cgi.escape(block['course_name']),
        display_name=cgi.escape(block['display_name']),
        question_text=cgi.escape(block['question_text']),
        zone0_title=cgi.escape(block['zones'][0]['title']) if block['zones'] else '',
        zone1_title=cgi.escape(block['zones'][1]['title']) if len(block['zones']) > 1 else '',
        item0_name=cgi.escape(block['items'][0]['displayName']) if block['items'] else '',
        item1_name=cgi.escape(block['items'][1]['displayName']) if len(block['items']) > 1 else ''
    )


@app.route('/learn/<block_id>')
def view_block(block_id):
    """Student view of course block - renders content for learning"""
    if block_id not in course_blocks:
        return "Block not found", 404
    
    block = course_blocks[block_id]
    
    # Build zones HTML - renders zone titles (VULNERABLE: no sanitization on output)
    zones_html = ""
    for zone in block['zones']:
        # Zone titles are rendered with innerHTML in the frontend
        zones_html += '<div class="drop-zone" data-zone-id="{0}"><div class="zone-title">{1}</div></div>'.format(
            zone['id'], zone['title']
        )
    
    # Build items HTML - item names are sanitized
    items_html = ""
    for item in block['items']:
        items_html += '<div class="drag-item" draggable="true" data-item-id="{0}">{1}</div>'.format(
            item['id'], cgi.escape(item['displayName'])
        )
    
    # The display_name and zone titles are rendered without escaping (vulnerable)
    page_content = STUDENT_VIEW_CONTENT.format(
        display_name=block['display_name'],  # VULNERABLE: not escaped
        question_text=cgi.escape(block['question_text']),  # Safe: escaped
        zones_html=zones_html,  # Contains unescaped zone titles
        items_html=items_html,  # Safe: item names escaped
        course_name=cgi.escape(block['course_name'])  # Safe: escaped
    )
    
    # Check for XSS execution (simulates browser rendering)
    result = check_xss(page_content, flags[0], block['display_name'] + ''.join(z['title'] for z in block['zones']), 'xss_easy_med')
    
    # If XSS detected, include flag
    if result == 'XSS':
        success_msg = '<div class="alert alert-success">Congratulations! Security audit passed. Flag: {0}</div>'.format(flags[0])
        page_content = STUDENT_VIEW_CONTENT.format(
            display_name=block['display_name'],
            question_text=cgi.escape(block['question_text']),
            zones_html=zones_html,
            items_html=items_html,
            course_name=cgi.escape(block['course_name'])
        ).replace('</body>', success_msg + '</body>')
    
    response = make_response(page_content)
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/api/block/<block_id>/data')
def block_data(block_id):
    """API endpoint returning block data for frontend rendering"""
    if block_id not in course_blocks:
        return jsonify({"error": "Block not found"}), 404
    
    block = course_blocks[block_id]
    
    # Return data that will be rendered client-side
    return jsonify({
        "id": block["id"],
        "display_name": block["display_name"],
        "question_text": block["question_text"],
        "zones": block["zones"],
        "items": block["items"]
    })


@app.route('/help')
def help_page():
    return HELP_CONTENT


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - instructors need to authenticate"""
    if request.method == 'POST':
        # Simple auth for demo
        return redirect('/studio')
    return LOGIN_CONTENT


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Feedback form - input is properly sanitized"""
    if request.method == 'POST':
        # Feedback is sanitized
        fb = sanitize_html(request.form.get('feedback', ''))
        return FEEDBACK_RESPONSE.format(cgi.escape(fb))
    return FEEDBACK_FORM


if __name__ == '__main__':
    app.run(debug=True)
