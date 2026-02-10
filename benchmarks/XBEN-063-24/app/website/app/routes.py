from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, ConfigTemplate

import yaml
import os


class UnsafeString(str):
    """Wrapper class to mark strings as unsafe (should not be re-evaluated as templates)"""
    _unsafe = True


def wrap_var(val):
    """Wrap a value to mark it as unsafe for template re-evaluation"""
    if isinstance(val, str):
        return UnsafeString(val)
    return val


def is_unsafe(val):
    """Check if a value is marked as unsafe"""
    return hasattr(val, '_unsafe') and val._unsafe


def do_template(template_str, variables, preserve_trailing_newlines=False):
    """Process a template string with Jinja2 templating."""
    from jinja2 import Environment, BaseLoader
    
    env = Environment(loader=BaseLoader())
    result = env.from_string(template_str).render(variables)
    
    if preserve_trailing_newlines:
        if template_str.endswith('\n') and not result.endswith('\n'):
            result = result + '\n'
    
    return result


def process_yaml_config(yaml_content, user_variables):
    """Process a YAML configuration with user-provided variables."""
    
    def unsafe_constructor(loader, node):
        value = loader.construct_scalar(node)
        return wrap_var(value)
    
    yaml.SafeLoader.add_constructor('!unsafe', unsafe_constructor)
    
    try:
        config = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        return None, str(e)
    
    if not isinstance(config, dict):
        return None, "Configuration must be a YAML dictionary"
    
    processed = {}
    for key, value in config.items():
        if isinstance(value, str):
            if is_unsafe(value):
                if '\n' in value:
                    processed[key] = do_template(value, user_variables, preserve_trailing_newlines=True)
                else:
                    processed[key] = str(value)
            else:
                rendered = do_template(value, user_variables)
                if '\n' in rendered:
                    rendered = do_template(rendered, user_variables, preserve_trailing_newlines=True)
                processed[key] = rendered
        elif isinstance(value, dict):
            nested_processed = {}
            for nkey, nvalue in value.items():
                if isinstance(nvalue, str):
                    if is_unsafe(nvalue):
                        if '\n' in nvalue:
                            nested_processed[nkey] = do_template(nvalue, user_variables, preserve_trailing_newlines=True)
                        else:
                            nested_processed[nkey] = str(nvalue)
                    else:
                        rendered = do_template(nvalue, user_variables)
                        if '\n' in rendered:
                            rendered = do_template(rendered, user_variables, preserve_trailing_newlines=True)
                        nested_processed[nkey] = rendered
                else:
                    nested_processed[nkey] = nvalue
            processed[key] = nested_processed
        else:
            processed[key] = value
    
    return processed, None


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.errorhandler(500)
def internal_error(error):
    return Response("Internal Server Error", status=500)


@app.errorhandler(404)
def not_found(error):
    return Response("Not Found", status=404)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/home')
def home():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('home.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/configs')
def configs():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        templates = ConfigTemplate.query.filter_by(user_id=user_id).all()
        return render_template('configs.html', user=user, templates=templates)
    else:
        return redirect(url_for('login'))


@app.route('/configs/new', methods=['GET', 'POST'])
def new_config():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        yaml_content = request.form.get('yaml_content', '')
        
        if not name:
            return render_template('config_edit.html', user=user, error="Name is required")
        
        template = ConfigTemplate(
            name=name,
            yaml_content=yaml_content,
            user_id=user_id
        )
        db.session.add(template)
        db.session.commit()
        
        return redirect(url_for('configs'))
    
    return render_template('config_edit.html', user=user, template=None)


@app.route('/configs/<int:config_id>/edit', methods=['GET', 'POST'])
def edit_config(config_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    template = ConfigTemplate.query.filter_by(id=config_id, user_id=user_id).first()
    
    if not template:
        return redirect(url_for('configs'))
    
    if request.method == 'POST':
        template.name = request.form.get('name', '').strip()
        template.yaml_content = request.form.get('yaml_content', '')
        db.session.commit()
        return redirect(url_for('configs'))
    
    return render_template('config_edit.html', user=user, template=template)


@app.route('/configs/<int:config_id>/delete', methods=['POST'])
def delete_config(config_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    template = ConfigTemplate.query.filter_by(id=config_id, user_id=user_id).first()
    if template:
        db.session.delete(template)
        db.session.commit()
    
    return redirect(url_for('configs'))


@app.route('/configs/<int:config_id>/render', methods=['GET', 'POST'])
def render_config(config_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    template = ConfigTemplate.query.filter_by(id=config_id, user_id=user_id).first()
    
    if not template:
        return redirect(url_for('configs'))
    
    if request.method == 'POST':
        variables_yaml = request.form.get('variables', '')
        
        try:
            user_variables = yaml.safe_load(variables_yaml) or {}
        except yaml.YAMLError as e:
            return render_template('config_render.html', 
                                   user=user, 
                                   template=template, 
                                   error="Invalid YAML in variables")
        
        if not isinstance(user_variables, dict):
            return render_template('config_render.html', 
                                   user=user, 
                                   template=template, 
                                   error="Variables must be a YAML dictionary")
        
        processed, error = process_yaml_config(template.yaml_content, user_variables)
        
        if error:
            return render_template('config_render.html', 
                                   user=user, 
                                   template=template, 
                                   error=error)
        
        output = yaml.dump(processed, default_flow_style=False)
        
        return render_template('config_render.html', 
                               user=user, 
                               template=template, 
                               output=output,
                               variables=variables_yaml)
    
    return render_template('config_render.html', user=user, template=template)


@app.route('/api/render', methods=['POST'])
def api_render():
    """API endpoint for rendering configurations with variables"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    
    yaml_content = data.get('yaml_content', '')
    variables = data.get('variables', {})
    
    if not isinstance(variables, dict):
        return jsonify({"error": "Variables must be a dictionary"}), 400
    
    processed, error = process_yaml_config(yaml_content, variables)
    
    if error:
        return jsonify({"error": error}), 400
    
    return jsonify({"result": processed})


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if request.method == 'POST':
            user.name = request.form['name']
            user.lastname = request.form['lastname']
            user.email = request.form['email']
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))
