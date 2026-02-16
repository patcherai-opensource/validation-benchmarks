import os
import dis
import functools
from decimal import Decimal
from flask import Flask, request, jsonify, render_template, flash, redirect, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workspace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# --- Models ---

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    workspaces = db.relationship('Workspace', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Workspace(db.Model):
    __tablename__ = 'workspaces'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default='')
    model_type = db.Column(db.String(80), default='document')
    filter_expr = db.Column(db.String(500), default='[]')
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    children = db.relationship('Workspace', backref=db.backref('parent', remote_side=[id]), lazy=True)
    documents = db.relationship('Document', backref='workspace', lazy=True)


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, default='')
    doc_type = db.Column(db.String(50), default='text')
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# --- Filter Expression Evaluator ---
# Evaluates workspace filter expressions safely by restricting available
# operations and preventing access to private attributes.

_PERMITTED_OPS = set()
for _opname in [
    'POP_TOP', 'RESUME', 'PUSH_NULL', 'NOP',
    'BUILD_LIST', 'BUILD_MAP', 'BUILD_TUPLE', 'BUILD_SET',
    'BUILD_CONST_KEY_MAP', 'BUILD_STRING', 'LIST_EXTEND',
    'LOAD_CONST', 'RETURN_VALUE', 'RETURN_CONST',
    'STORE_SUBSCR', 'BINARY_SUBSCR',
    'UNARY_NEGATIVE', 'UNARY_NOT', 'UNARY_INVERT',
    'BINARY_OP', 'COMPARE_OP', 'CONTAINS_OP', 'IS_OP',
    'LOAD_NAME', 'STORE_NAME', 'DELETE_NAME',
    'LOAD_ATTR', 'LOAD_GLOBAL',
    'CALL', 'CALL_FUNCTION', 'CALL_FUNCTION_EX',
    'GET_ITER', 'FOR_ITER', 'LIST_APPEND',
    'JUMP_FORWARD', 'JUMP_BACKWARD', 'JUMP_ABSOLUTE',
    'POP_JUMP_IF_FALSE', 'POP_JUMP_IF_TRUE',
    'POP_JUMP_IF_NONE', 'POP_JUMP_IF_NOT_NONE',
    'COPY', 'SWAP', 'RERAISE',
    'MAKE_FUNCTION', 'LOAD_FAST', 'STORE_FAST',
    'LOAD_FAST_AND_CLEAR', 'LOAD_FAST_CHECK',
    'KW_NAMES', 'PRECALL',
    'END_FOR', 'END_SEND',
]:
    if _opname in dis.opmap:
        _PERMITTED_OPS.add(dis.opmap[_opname])


def _compile_expression(source):
    comp = compile(source, '<filter>', 'eval')
    for instr in dis.get_instructions(comp):
        if instr.opcode not in _PERMITTED_OPS:
            raise ValueError('Operation %s is not permitted in filter expressions' % instr.opname)
    # Also check nested code objects (comprehensions)
    for const in comp.co_consts:
        if hasattr(const, 'co_code'):
            for instr in dis.get_instructions(const):
                if instr.opcode not in _PERMITTED_OPS:
                    raise ValueError('Operation %s is not permitted in filter expressions' % instr.opname)
    return comp


def evaluate_filter(source, data=None):
    """
    Evaluate a filter expression string in a restricted environment.
    Only allows safe operations for building filter criteria.
    Prevents access to private/dunder attributes by rejecting
    double-underscore sequences in the expression source.
    """
    if not isinstance(source, str):
        raise TypeError('Filter expression must be a string')

    if '__' in source:
        raise ValueError('Double underscores are not allowed in filter expressions')

    comp = _compile_expression(source)
    return eval(comp, {'__builtins__': {
        'True': True,
        'False': False,
        'None': None,
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'list': list,
        'tuple': tuple,
        'dict': dict,
        'len': len,
        'round': round,
        'Decimal': Decimal,
        'type': type,
        'getattr': getattr,
        'hasattr': hasattr,
        'globals': locals,
        'locals': locals,
    }}, data or {})


# --- Auth Helpers ---

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


# --- Routes ---

@app.route('/')
def index():
    user = get_current_user()
    if user:
        return redirect('/workspaces')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, is_active=True).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect('/workspaces')
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/workspaces')
@login_required
def list_workspaces():
    user = get_current_user()
    workspaces = Workspace.query.filter_by(owner_id=user.id, parent_id=None).all()
    return render_template('workspaces.html', workspaces=workspaces, user=user)


@app.route('/workspace/new', methods=['GET', 'POST'])
@login_required
def create_workspace():
    user = get_current_user()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        model_type = request.form.get('model_type', 'document').strip()
        filter_expr = request.form.get('filter_expr', '[]').strip()
        parent_id = request.form.get('parent_id')
        if not name:
            flash('Workspace name is required.', 'danger')
            return render_template('workspace_form.html', user=user, workspace=None)

        ws = Workspace(
            name=name,
            description=description,
            model_type=model_type,
            filter_expr=filter_expr,
            owner_id=user.id,
            parent_id=int(parent_id) if parent_id else None,
        )
        db.session.add(ws)
        db.session.commit()
        flash('Workspace created.', 'success')
        return redirect('/workspaces')
    return render_template('workspace_form.html', user=user, workspace=None)


@app.route('/workspace/<int:ws_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workspace(ws_id):
    user = get_current_user()
    ws = Workspace.query.filter_by(id=ws_id, owner_id=user.id).first_or_404()
    if request.method == 'POST':
        ws.name = request.form.get('name', ws.name).strip()
        ws.description = request.form.get('description', ws.description).strip()
        ws.model_type = request.form.get('model_type', ws.model_type).strip()
        ws.filter_expr = request.form.get('filter_expr', ws.filter_expr).strip()
        db.session.commit()
        flash('Workspace updated.', 'success')
        return redirect(f'/workspace/{ws.id}')
    return render_template('workspace_form.html', user=user, workspace=ws)


@app.route('/workspace/<int:ws_id>/delete', methods=['POST'])
@login_required
def delete_workspace(ws_id):
    user = get_current_user()
    ws = Workspace.query.filter_by(id=ws_id, owner_id=user.id).first_or_404()
    db.session.delete(ws)
    db.session.commit()
    flash('Workspace deleted.', 'success')
    return redirect('/workspaces')


@app.route('/workspace/<int:ws_id>')
@login_required
def view_workspace(ws_id):
    user = get_current_user()
    ws = Workspace.query.filter_by(id=ws_id, owner_id=user.id).first_or_404()
    documents = []
    filter_result = None
    filter_error = None

    try:
        criteria = evaluate_filter(ws.filter_expr or '[]')
        if isinstance(criteria, list) and len(criteria) > 0:
            query = Document.query.filter_by(workspace_id=ws.id)
            for criterion in criteria:
                if isinstance(criterion, (list, tuple)) and len(criterion) == 3:
                    field, op, value = criterion
                    col = getattr(Document, field, None)
                    if col is not None:
                        if op == '=':
                            query = query.filter(col == value)
                        elif op == '!=':
                            query = query.filter(col != value)
                        elif op == 'like':
                            query = query.filter(col.like(value))
                        elif op == 'in':
                            query = query.filter(col.in_(value))
            documents = query.all()
        else:
            documents = Document.query.filter_by(workspace_id=ws.id).all()
        filter_result = str(criteria)
    except Exception as e:
        filter_error = str(e)
        documents = Document.query.filter_by(workspace_id=ws.id).all()

    children = Workspace.query.filter_by(parent_id=ws.id, owner_id=user.id).all()
    return render_template('workspace_view.html',
                           workspace=ws, documents=documents,
                           children=children, user=user,
                           filter_result=filter_result,
                           filter_error=filter_error)


@app.route('/workspace/<int:ws_id>/document/new', methods=['GET', 'POST'])
@login_required
def create_document(ws_id):
    user = get_current_user()
    ws = Workspace.query.filter_by(id=ws_id, owner_id=user.id).first_or_404()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        content = request.form.get('content', '')
        doc_type = request.form.get('doc_type', 'text').strip()
        if not name:
            flash('Document name is required.', 'danger')
            return render_template('document_form.html', user=user, workspace=ws, document=None)
        doc = Document(name=name, content=content, doc_type=doc_type, workspace_id=ws.id)
        db.session.add(doc)
        db.session.commit()
        flash('Document created.', 'success')
        return redirect(f'/workspace/{ws.id}')
    return render_template('document_form.html', user=user, workspace=ws, document=None)


@app.route('/workspace/<int:ws_id>/document/<int:doc_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_document(ws_id, doc_id):
    user = get_current_user()
    ws = Workspace.query.filter_by(id=ws_id, owner_id=user.id).first_or_404()
    doc = Document.query.filter_by(id=doc_id, workspace_id=ws.id).first_or_404()
    if request.method == 'POST':
        doc.name = request.form.get('name', doc.name).strip()
        doc.content = request.form.get('content', doc.content)
        doc.doc_type = request.form.get('doc_type', doc.doc_type).strip()
        db.session.commit()
        flash('Document updated.', 'success')
        return redirect(f'/workspace/{ws.id}')
    return render_template('document_form.html', user=user, workspace=ws, document=doc)


@app.route('/workspace/<int:ws_id>/document/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_document(ws_id, doc_id):
    user = get_current_user()
    ws = Workspace.query.filter_by(id=ws_id, owner_id=user.id).first_or_404()
    doc = Document.query.filter_by(id=doc_id, workspace_id=ws.id).first_or_404()
    db.session.delete(doc)
    db.session.commit()
    flash('Document deleted.', 'success')
    return redirect(f'/workspace/{ws.id}')


@app.route('/ping')
def ping():
    return 'OK', 200


# --- API Endpoints ---

@app.route('/api/workspace/<int:ws_id>/documents')
@login_required
def api_list_documents(ws_id):
    user = get_current_user()
    ws = Workspace.query.filter_by(id=ws_id, owner_id=user.id).first()
    if not ws:
        return jsonify({'error': 'Workspace not found'}), 404

    try:
        criteria = evaluate_filter(ws.filter_expr or '[]')
        documents = Document.query.filter_by(workspace_id=ws.id).all()
        return jsonify({
            'workspace': ws.name,
            'filter_applied': str(criteria),
            'documents': [{'id': d.id, 'name': d.name, 'type': d.doc_type} for d in documents]
        })
    except Exception as e:
        return jsonify({'error': 'Filter evaluation failed', 'detail': str(e)}), 400


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='The requested resource was not found.'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='An internal error occurred.'), 500


# --- Initialization ---

def init_db():
    db.create_all()

    if User.query.count() == 0:
        admin = User(username='admin')
        admin.set_password('admin')
        db.session.add(admin)

        demo = User(username='demo')
        demo.set_password('demo')
        db.session.add(demo)
        db.session.commit()

        ws1 = Workspace(name='Project Documents', description='Main project workspace',
                        model_type='document', filter_expr='[]', owner_id=admin.id)
        ws2 = Workspace(name='Reports', description='Monthly and quarterly reports',
                        model_type='report', filter_expr='[]', owner_id=admin.id)
        db.session.add(ws1)
        db.session.add(ws2)
        db.session.commit()

        docs = [
            Document(name='README.md', content='# Project Overview\nWelcome to the workspace.', doc_type='text', workspace_id=ws1.id),
            Document(name='architecture.pdf', content='Architecture document placeholder', doc_type='pdf', workspace_id=ws1.id),
            Document(name='Q4-Report.xlsx', content='Quarterly report data', doc_type='spreadsheet', workspace_id=ws2.id),
        ]
        for d in docs:
            db.session.add(d)
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5003)
