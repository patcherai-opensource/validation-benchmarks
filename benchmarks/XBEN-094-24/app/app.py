import os
import dis
import logging
from datetime import datetime

from flask import (Flask, request, render_template, flash,
                   redirect, url_for)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, UserMixin, login_user, logout_user,
                         login_required, current_user)
import bcrypt

app = Flask(__name__)
app.secret_key = 'f7d3b9a2e1c4d8f6a5b0c7e9d2f4a6b8c1d3e5f7a9b2c4d6e8f0a1b3c5d7e9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trytond.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('trytond')


# --- Models ---

class User(UserMixin, db.Model):
    __tablename__ = 'res_user'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    active = db.Column(db.Boolean, default=True)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )


class Collection(db.Model):
    __tablename__ = 'webdav_collection'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    model = db.Column(db.String(256), nullable=True)
    domain = db.Column(db.Text, default='[]')
    complete_name = db.Column(db.String(512))
    parent_id = db.Column(db.Integer, db.ForeignKey('webdav_collection.id'), nullable=True)
    create_uid = db.Column(db.Integer, db.ForeignKey('res_user.id'))
    write_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship('User', foreign_keys=[create_uid])


class Resource(db.Model):
    __tablename__ = 'ir_resource'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    res_model = db.Column(db.String(256))
    description = db.Column(db.Text, default='')
    active = db.Column(db.Boolean, default=True)
    sequence = db.Column(db.Integer, default=10)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    write_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Attachment(db.Model):
    __tablename__ = 'ir_attachment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    res_model = db.Column(db.String(256))
    res_id = db.Column(db.Integer, default=0)
    data = db.Column(db.Text)
    description = db.Column(db.Text, default='')
    create_uid = db.Column(db.Integer, db.ForeignKey('res_user.id'))
    create_date = db.Column(db.DateTime, default=datetime.utcnow)


# --- safe_eval (Tryton-style restricted eval) ---

_SAFE_OPCODES = set([
    'LOAD_CONST', 'LOAD_NAME', 'LOAD_GLOBAL',
    'UNARY_POSITIVE', 'UNARY_NEGATIVE', 'UNARY_NOT', 'UNARY_INVERT',
    'BINARY_ADD', 'BINARY_SUBTRACT', 'BINARY_MULTIPLY',
    'BINARY_TRUE_DIVIDE', 'BINARY_FLOOR_DIVIDE', 'BINARY_MODULO',
    'BINARY_POWER', 'BINARY_SUBSCR',
    'BINARY_AND', 'BINARY_OR', 'BINARY_XOR',
    'BINARY_LSHIFT', 'BINARY_RSHIFT',
    'BUILD_LIST', 'BUILD_TUPLE', 'BUILD_MAP', 'BUILD_SET',
    'BUILD_CONST_KEY_MAP',
    'LIST_EXTEND', 'LIST_APPEND',
    'COMPARE_OP', 'CONTAINS_OP', 'IS_OP',
    'RETURN_VALUE', 'RETURN_CONST',
    'POP_TOP', 'NOP', 'COPY',
    'STORE_NAME', 'STORE_SUBSCR',
    'LOAD_ATTR', 'STORE_ATTR',
    'CALL_FUNCTION', 'CALL_FUNCTION_KW',
    'CALL', 'PUSH_NULL', 'PRECALL',
    'MAKE_FUNCTION', 'RESUME',
    'GET_ITER', 'FOR_ITER',
    'JUMP_FORWARD', 'JUMP_BACKWARD',
    'JUMP_IF_TRUE_OR_POP', 'JUMP_IF_FALSE_OR_POP',
    'POP_JUMP_IF_TRUE', 'POP_JUMP_IF_FALSE',
    'POP_JUMP_FORWARD_IF_TRUE', 'POP_JUMP_FORWARD_IF_FALSE',
    'POP_JUMP_FORWARD_IF_NONE', 'POP_JUMP_FORWARD_IF_NOT_NONE',
    'POP_JUMP_BACKWARD_IF_TRUE', 'POP_JUMP_BACKWARD_IF_FALSE',
    'POP_JUMP_IF_NONE', 'POP_JUMP_IF_NOT_NONE',
    'UNPACK_SEQUENCE',
    'BUILD_SLICE', 'FORMAT_VALUE', 'BUILD_STRING',
    'LOAD_FAST', 'STORE_FAST', 'DELETE_FAST',
    'LOAD_METHOD', 'CALL_METHOD',
    'MAP_ADD', 'SET_ADD',
    'DICT_MERGE', 'DICT_UPDATE',
    'LIST_TO_TUPLE',
    'KW_NAMES',
    'SWAP', 'CACHE',
    'EXTENDED_ARG',
    'END_FOR',
    'LOAD_FAST_AND_CLEAR',
    'LOAD_FAST_CHECK',
    'RERAISE',
    'LOAD_SUPER_ATTR',
    'CALL_INTRINSIC_1',
])


def safe_eval(expression, context=None):
    """Evaluate an expression safely.

    Restricts available builtins and checks bytecode opcodes to prevent
    dangerous operations. Only simple data-structure expressions and
    basic comparisons are allowed.
    """
    if context is None:
        context = {}

    if not isinstance(expression, str):
        raise ValueError("Expression must be a string")

    expression = expression.strip()
    if not expression:
        return []

    try:
        code = compile(expression, '<safe_eval>', 'eval')
    except SyntaxError:
        raise ValueError("Invalid expression syntax")

    # Check opcodes of the compiled code
    for instruction in dis.get_instructions(code):
        if instruction.opname not in _SAFE_OPCODES:
            raise ValueError(
                "Unsafe opcode: %s" % instruction.opname
            )

    _safe_builtins = {
        'True': True,
        'False': False,
        'None': None,
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'tuple': tuple,
        'dict': dict,
        'bool': bool,
        'len': len,
        'range': range,
        'sorted': sorted,
        'min': min,
        'max': max,
        'abs': abs,
        'sum': sum,
        'round': round,
        'enumerate': enumerate,
        'zip': zip,
        'map': map,
        'filter': filter,
        'any': any,
        'all': all,
        'set': set,
        'frozenset': frozenset,
        'isinstance': isinstance,
        'type': type,
        'getattr': getattr,
        'hasattr': hasattr,
        'chr': chr,
        'ord': ord,
    }

    safe_globals = {'__builtins__': _safe_builtins}
    safe_globals.update(context)

    return eval(code, safe_globals)


def apply_domain_filter(resources, domain_expr):
    """Apply a domain filter expression to a list of resources.

    The domain expression should evaluate to a list of filter tuples:
      [('field', 'operator', value), ...]

    Supported operators: '=', '!=', 'like', 'not like', 'in', 'not in'
    """
    try:
        domain = safe_eval(domain_expr)
    except Exception as e:
        logger.warning("Domain evaluation error: %s", e)
        return resources, str(e)

    if not isinstance(domain, list):
        return resources, "Domain must evaluate to a list, got: %s" % str(domain)[:500]

    filtered = resources
    for clause in domain:
        if not isinstance(clause, (list, tuple)) or len(clause) != 3:
            continue
        field, op, value = clause
        if not isinstance(field, str):
            continue

        new_filtered = []
        for r in filtered:
            attr = getattr(r, field, None)
            if attr is None:
                continue
            if op == '=' and attr == value:
                new_filtered.append(r)
            elif op == '!=' and attr != value:
                new_filtered.append(r)
            elif op == 'like' and isinstance(attr, str) and value in attr:
                new_filtered.append(r)
            elif op == 'not like' and isinstance(attr, str) and value not in attr:
                new_filtered.append(r)
            elif op == 'in' and attr in value:
                new_filtered.append(r)
            elif op == 'not in' and attr not in value:
                new_filtered.append(r)
        filtered = new_filtered

    return filtered, None


# --- Auth ---

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        login_name = request.form.get('login', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(login=login_name, active=True).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next', url_for('index'))
            return redirect(next_page)

        flash('Invalid credentials', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# --- Collection views ---

@app.route('/')
@login_required
def index():
    collections = Collection.query.all()
    return render_template('index.html', collections=collections)


@app.route('/collection/new', methods=['GET', 'POST'])
@login_required
def collection_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        model = request.form.get('model', '').strip()
        domain = request.form.get('domain', '[]').strip()

        if not name:
            flash('Collection name is required', 'danger')
            return render_template('collection_form.html', collection=None)

        collection = Collection(
            name=name,
            model=model or 'ir.resource',
            domain=domain,
            complete_name=name,
            create_uid=current_user.id,
        )
        db.session.add(collection)
        db.session.commit()
        flash('Collection created successfully', 'success')
        return redirect(url_for('collection_view', collection_id=collection.id))

    return render_template('collection_form.html', collection=None)


@app.route('/collection/<int:collection_id>')
@login_required
def collection_view(collection_id):
    collection = Collection.query.get_or_404(collection_id)

    resources = Resource.query.filter_by(active=True).all()
    error = None

    if collection.domain and collection.domain.strip() != '[]':
        resources, error = apply_domain_filter(resources, collection.domain)

    return render_template(
        'collection_view.html',
        collection=collection,
        resources=resources,
        error=error
    )


@app.route('/collection/<int:collection_id>/edit', methods=['GET', 'POST'])
@login_required
def collection_edit(collection_id):
    collection = Collection.query.get_or_404(collection_id)

    if request.method == 'POST':
        collection.name = request.form.get('name', collection.name).strip()
        collection.model = request.form.get('model', collection.model).strip()
        collection.domain = request.form.get('domain', collection.domain).strip()
        collection.complete_name = collection.name
        db.session.commit()
        flash('Collection updated', 'success')
        return redirect(url_for('collection_view', collection_id=collection.id))

    return render_template('collection_form.html', collection=collection)


@app.route('/collection/<int:collection_id>/delete', methods=['POST'])
@login_required
def collection_delete(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    db.session.delete(collection)
    db.session.commit()
    flash('Collection deleted', 'success')
    return redirect(url_for('index'))


# --- Resource views ---

@app.route('/resources')
@login_required
def resource_list():
    resources = Resource.query.filter_by(active=True).order_by(Resource.sequence).all()
    return render_template('resource_list.html', resources=resources)


@app.route('/resource/new', methods=['GET', 'POST'])
@login_required
def resource_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        res_model = request.form.get('res_model', '').strip()
        description = request.form.get('description', '').strip()
        sequence = request.form.get('sequence', '10')

        if not name:
            flash('Resource name is required', 'danger')
            return render_template('resource_form.html', resource=None)

        resource = Resource(
            name=name,
            res_model=res_model or 'ir.resource',
            description=description,
            sequence=int(sequence) if sequence.isdigit() else 10,
        )
        db.session.add(resource)
        db.session.commit()
        flash('Resource created', 'success')
        return redirect(url_for('resource_list'))

    return render_template('resource_form.html', resource=None)


@app.route('/resource/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
def resource_edit(resource_id):
    resource = Resource.query.get_or_404(resource_id)

    if request.method == 'POST':
        resource.name = request.form.get('name', resource.name).strip()
        resource.res_model = request.form.get('res_model', resource.res_model).strip()
        resource.description = request.form.get('description', resource.description).strip()
        seq = request.form.get('sequence', str(resource.sequence))
        resource.sequence = int(seq) if seq.isdigit() else resource.sequence
        db.session.commit()
        flash('Resource updated', 'success')
        return redirect(url_for('resource_list'))

    return render_template('resource_form.html', resource=resource)


@app.route('/resource/<int:resource_id>/delete', methods=['POST'])
@login_required
def resource_delete(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    resource.active = False
    db.session.commit()
    flash('Resource archived', 'success')
    return redirect(url_for('resource_list'))


# --- Attachment views ---

@app.route('/attachments')
@login_required
def attachment_list():
    attachments = Attachment.query.order_by(Attachment.create_date.desc()).all()
    return render_template('attachment_list.html', attachments=attachments)


@app.route('/attachment/new', methods=['GET', 'POST'])
@login_required
def attachment_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        res_model = request.form.get('res_model', '').strip()
        data = request.form.get('data', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Attachment name is required', 'danger')
            return render_template('attachment_form.html', attachment=None)

        attachment = Attachment(
            name=name,
            res_model=res_model or 'ir.attachment',
            data=data,
            description=description,
            create_uid=current_user.id,
        )
        db.session.add(attachment)
        db.session.commit()
        flash('Attachment created', 'success')
        return redirect(url_for('attachment_list'))

    return render_template('attachment_form.html', attachment=None)


# --- Error handlers ---

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500


# --- Database initialization ---

def init_db():
    db.create_all()

    if not User.query.filter_by(login='admin').first():
        admin = User(login='admin', name='Administrator')
        admin.set_password('admin')
        db.session.add(admin)

        demo = User(login='demo', name='Demo User')
        demo.set_password('demo')
        db.session.add(demo)
        db.session.commit()

    if Resource.query.count() == 0:
        sample_resources = [
            Resource(name='Party', res_model='party.party',
                     description='Party/Contact management', sequence=1),
            Resource(name='Product', res_model='product.product',
                     description='Product catalog entries', sequence=2),
            Resource(name='Sale Order', res_model='sale.sale',
                     description='Sales order records', sequence=3),
            Resource(name='Invoice', res_model='account.invoice',
                     description='Customer and supplier invoices', sequence=4),
            Resource(name='Stock Move', res_model='stock.move',
                     description='Inventory movement records', sequence=5),
            Resource(name='Purchase Order', res_model='purchase.purchase',
                     description='Purchase order tracking', sequence=6),
            Resource(name='Payment', res_model='account.payment',
                     description='Payment transaction records', sequence=7),
            Resource(name='Employee', res_model='company.employee',
                     description='Employee directory', sequence=8),
            Resource(name='Project', res_model='project.work',
                     description='Project management entries', sequence=9),
            Resource(name='Timesheet', res_model='timesheet.line',
                     description='Work timesheet entries', sequence=10),
        ]
        db.session.add_all(sample_resources)
        db.session.commit()

    if Collection.query.count() == 0:
        c1 = Collection(
            name='All Resources',
            model='ir.resource',
            domain='[]',
            complete_name='All Resources',
            create_uid=1,
        )
        c2 = Collection(
            name='Sales Documents',
            model='ir.resource',
            domain="[('res_model', 'like', 'sale')]",
            complete_name='Sales Documents',
            create_uid=1,
        )
        c3 = Collection(
            name='Financial Records',
            model='ir.resource',
            domain="[('res_model', 'like', 'account')]",
            complete_name='Financial Records',
            create_uid=1,
        )
        db.session.add_all([c1, c2, c3])
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5003, debug=False)
