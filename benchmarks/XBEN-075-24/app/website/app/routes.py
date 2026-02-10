from flask import Flask, render_template, redirect, url_for, request, make_response

from app import app
from app.models import UrlObj
from uuid import uuid4
import pickle
import base64
import json

BIN_PREFIX = "b64~"

def str_to_object(value):
    """
    Deserialize string value to Python object.
    Values starting with 'b64~' are treated as base64-encoded serialized objects.
    """
    if value is None:
        return None
    
    if value.startswith(BIN_PREFIX):
        encoded_data = value[len(BIN_PREFIX):]
        try:
            data = base64.b64decode(encoded_data)
            return pickle.loads(data)
        except Exception:
            return None
    
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

def object_to_str(obj):
    """
    Serialize Python object to string for storage.
    """
    return json.dumps(obj, default=lambda o: {'name': o.name, 'url': o.url})

def name_in_list(urls, name):
    if not isinstance(urls, list):
        return False
    return any(isinstance(u, dict) and u.get('name') == name for u in urls)

def remove_url_with_name(urls, name):
    if not isinstance(urls, list):
        return False
    for i, u in enumerate(urls):
        if isinstance(u, dict) and u.get('name') == name:
            del urls[i]
            return True 
    return False 

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    return redirect(url_for('bookmarks_list'))

@app.route('/list')
def bookmarks_list():
    bookmarks_cookie = request.cookies.get('bookmarks')
    user_cookie = request.cookies.get('user')
    
    if bookmarks_cookie and user_cookie:
        urls = str_to_object(bookmarks_cookie)
        if urls is None:
            urls = []
        user = user_cookie
    else:
        urls = []
        user = uuid4().hex
        response = make_response(render_template('list_urls.html', urls=urls, user=user))
        response.set_cookie('bookmarks', object_to_str([]))
        response.set_cookie('user', user)
        return response
    
    return render_template('list_urls.html', urls=urls, user=user)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html')
    
    bookmarks_cookie = request.cookies.get('bookmarks')
    user_cookie = request.cookies.get('user')
    
    if bookmarks_cookie and user_cookie:
        name = request.form.get('name')
        url = request.form.get('url')
        
        urls = str_to_object(bookmarks_cookie)
        if urls is None:
            urls = []
        
        if name_in_list(urls, name):
            return render_template('add.html', error='Name already used')
        
        user = user_cookie
        urls.append({'name': name, 'url': url})
        
        response = make_response(render_template('list_urls.html', urls=urls, user=user))
        response.set_cookie('bookmarks', object_to_str(urls))
        response.set_cookie('user', user)
        return response 
    else:
        return redirect(url_for('bookmarks_list'))  

@app.route('/delete')
def delete():
    if not request.args.get('name'):
        return redirect(url_for('bookmarks_list'))
    
    bookmarks_cookie = request.cookies.get('bookmarks')
    user_cookie = request.cookies.get('user')
    
    if not bookmarks_cookie or not user_cookie:
        return redirect(url_for('bookmarks_list'))
    
    url_name = request.args.get('name')
    urls = str_to_object(bookmarks_cookie)
    user = user_cookie
    
    if urls is None:
        urls = []
    
    if remove_url_with_name(urls, url_name):
        response = make_response(render_template('list_urls.html', urls=urls, user=user))
        response.set_cookie('bookmarks', object_to_str(urls))
        response.set_cookie('user', user)
        return response 
    
    return redirect(url_for('bookmarks_list'))


@app.route('/about')
def about():
    if request.method == 'GET':
        return render_template('about.html')
