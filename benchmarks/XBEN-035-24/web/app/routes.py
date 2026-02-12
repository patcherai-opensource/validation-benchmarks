from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/docs')
def docs():
    return render_template('docs.html')


@main_bp.route('/ping')
def ping():
    return 'OK', 200
