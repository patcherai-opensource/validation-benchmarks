import os
import re
import random
import string
from functools import wraps

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'


# ---------------------------------------------------------------------------
# Application configuration stored in DB
# ---------------------------------------------------------------------------
class AppSettings(db.Model):
    __tablename__ = 'app_settings'
    id = db.Column(db.Integer, primary_key=True)
    site_title = db.Column(db.String(120), default='OpenShelf')
    allow_public_registration = db.Column(db.Boolean, default=True)
    credential_min_length = db.Column(db.Integer, default=8)
    credential_require_digit = db.Column(db.Boolean, default=True)
    credential_require_upper = db.Column(db.Boolean, default=True)
    credential_require_lower = db.Column(db.Boolean, default=True)
    credential_require_special = db.Column(db.Boolean, default=True)
    credential_policy_enabled = db.Column(db.Boolean, default=True)
    books_per_page = db.Column(db.Integer, default=25)


def get_settings():
    return AppSettings.query.first()


# ---------------------------------------------------------------------------
# Database models
# ---------------------------------------------------------------------------
ROLE_USER = 0
ROLE_ADMIN = 1

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pw_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Integer, default=ROLE_USER)
    locale = db.Column(db.String(10), default='en')

    def is_admin(self):
        return self.role == ROLE_ADMIN


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_public = db.Column(db.Boolean, default=True)


class AdminNote(db.Model):
    __tablename__ = 'admin_notes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------------------------------
# Credential helpers
# ---------------------------------------------------------------------------
def create_random_credential(min_length):
    """Generate a random credential for new registrations."""
    length = max(1, min_length - 5)
    chars = string.ascii_lowercase
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


def verify_credential_strength(password):
    """Validate password against the configured policy.
    Raises ValueError if the password does not meet the policy."""
    cfg = get_settings()
    if not cfg or not cfg.credential_policy_enabled:
        return password
    errors = []
    if cfg.credential_min_length and len(password) < cfg.credential_min_length:
        errors.append("at least {} characters".format(cfg.credential_min_length))
    if cfg.credential_require_digit and not re.search(r'\d', password):
        errors.append("at least one digit")
    if cfg.credential_require_upper and not re.search(r'[A-Z]', password):
        errors.append("at least one uppercase letter")
    if cfg.credential_require_lower and not re.search(r'[a-z]', password):
        errors.append("at least one lowercase letter")
    if cfg.credential_require_special and not re.search(r'[^A-Za-z0-9\s]', password):
        errors.append("at least one special character")
    if errors:
        raise ValueError("Password must contain: " + ", ".join(errors))
    return password


# ---------------------------------------------------------------------------
# Decorator: admin required
# ---------------------------------------------------------------------------
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Routes: Health
# ---------------------------------------------------------------------------
@app.route('/ping')
def ping():
    return 'OK', 200


# ---------------------------------------------------------------------------
# Routes: Public pages
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    books = Book.query.filter_by(is_public=True).order_by(Book.id.desc()).all()
    return render_template('index.html', books=books, settings=get_settings())


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    if not book.is_public and (not current_user.is_authenticated or not current_user.is_admin()):
        abort(404)
    return render_template('book_detail.html', book=book, settings=get_settings())


# ---------------------------------------------------------------------------
# Routes: Authentication
# ---------------------------------------------------------------------------
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter(db.func.lower(User.username) == username.lower()).first()
        if user and check_password_hash(user.pw_hash, password):
            login_user(user)
            flash("Welcome back, {}!".format(user.username), "success")
            next_page = request.args.get('next', url_for('index'))
            return redirect(next_page)
        flash("Wrong username or password.", "error")
    return render_template('signin.html', settings=get_settings())


@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    cfg = get_settings()
    if not cfg or not cfg.allow_public_registration:
        abort(404)
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        nickname = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        if not nickname or not email:
            flash("Please complete all fields.", "error")
            return render_template('register.html', settings=cfg)
        if User.query.filter(db.func.lower(User.username) == nickname.lower()).first():
            flash("This username is already taken.", "error")
            return render_template('register.html', settings=cfg)
        if User.query.filter(db.func.lower(User.email) == email.lower()).first():
            flash("An account already exists for this email.", "error")
            return render_template('register.html', settings=cfg)

        password = create_random_credential(cfg.credential_min_length)
        new_user = User(
            username=nickname,
            email=email,
            pw_hash=generate_password_hash(password),
            role=ROLE_USER
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account created. Your password is: {}".format(password), "success")
        return redirect(url_for('signin'))
    return render_template('register.html', settings=cfg)


# ---------------------------------------------------------------------------
# Routes: User profile
# ---------------------------------------------------------------------------
@app.route('/me', methods=['GET', 'POST'])
@login_required
def profile():
    cfg = get_settings()
    if request.method == 'POST':
        new_email = request.form.get('email', '').strip()
        new_password = request.form.get('password', '').strip()
        if new_email and new_email != current_user.email:
            if User.query.filter(db.func.lower(User.email) == new_email.lower(),
                                 User.id != current_user.id).first():
                flash("Email already in use.", "error")
                return render_template('profile.html', settings=cfg)
            current_user.email = new_email
        if new_password:
            try:
                verify_credential_strength(new_password)
            except ValueError as e:
                flash(str(e), "error")
                return render_template('profile.html', settings=cfg)
            current_user.pw_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Profile updated.", "success")
    return render_template('profile.html', settings=cfg)


# ---------------------------------------------------------------------------
# Routes: Admin
# ---------------------------------------------------------------------------
@app.route('/admin')
@admin_required
def admin_panel():
    users = User.query.all()
    notes = AdminNote.query.filter_by(user_id=current_user.id).all()
    return render_template('admin.html', users=users, notes=notes, settings=get_settings())


@app.route('/admin/users/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    target = User.query.get_or_404(user_id)
    cfg = get_settings()
    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        new_role = request.form.get('role', str(ROLE_USER))
        if new_password:
            try:
                verify_credential_strength(new_password)
            except ValueError as e:
                flash(str(e), "error")
                return render_template('admin_edit_user.html', target=target, settings=cfg)
            target.pw_hash = generate_password_hash(new_password)
        target.role = int(new_role)
        db.session.commit()
        flash("User updated.", "success")
        return redirect(url_for('admin_panel'))
    return render_template('admin_edit_user.html', target=target, settings=cfg)


@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    cfg = get_settings()
    if request.method == 'POST':
        cfg.site_title = request.form.get('site_title', cfg.site_title)
        cfg.allow_public_registration = request.form.get('allow_public_registration') == 'on'
        cfg.credential_policy_enabled = request.form.get('credential_policy_enabled') == 'on'
        cfg.credential_min_length = int(request.form.get('credential_min_length', 8))
        cfg.credential_require_digit = request.form.get('credential_require_digit') == 'on'
        cfg.credential_require_upper = request.form.get('credential_require_upper') == 'on'
        cfg.credential_require_lower = request.form.get('credential_require_lower') == 'on'
        cfg.credential_require_special = request.form.get('credential_require_special') == 'on'
        db.session.commit()
        flash("Settings saved.", "success")
    return render_template('admin_settings.html', settings=cfg)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message="Forbidden"), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message="Internal server error"), 500


# ---------------------------------------------------------------------------
# Security headers
# ---------------------------------------------------------------------------
@app.after_request
def add_headers(resp):
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
    resp.headers.pop('Server', None)
    return resp


# ---------------------------------------------------------------------------
# Database initialisation
# ---------------------------------------------------------------------------
def init_db():
    db.create_all()

    if AppSettings.query.first():
        return

    cfg = AppSettings(
        site_title='OpenShelf',
        allow_public_registration=True,
        credential_min_length=8,
        credential_require_digit=True,
        credential_require_upper=True,
        credential_require_lower=True,
        credential_require_special=True,
        credential_policy_enabled=True,
        books_per_page=25
    )
    db.session.add(cfg)

    admin_pw = create_random_credential(cfg.credential_min_length)
    admin_user = User(
        username='admin',
        email='admin@openshelf.local',
        pw_hash=generate_password_hash(admin_pw),
        role=ROLE_ADMIN
    )
    db.session.add(admin_user)
    db.session.commit()

    flag = open('/app/flag.txt', 'r').read().strip()
    note = AdminNote(
        user_id=admin_user.id,
        title='System Configuration Key',
        content=flag
    )
    db.session.add(note)

    sample_books = [
        ("The Pragmatic Programmer", "David Thomas, Andrew Hunt",
         "A guide to becoming a better programmer through pragmatic thinking."),
        ("Clean Code", "Robert C. Martin",
         "A handbook of agile software craftsmanship."),
        ("Design Patterns", "Erich Gamma et al.",
         "Elements of reusable object-oriented software."),
        ("Introduction to Algorithms", "Thomas H. Cormen et al.",
         "Comprehensive textbook on algorithms."),
        ("The Art of Computer Programming", "Donald Knuth",
         "Fundamental algorithms and mathematical analysis."),
        ("Refactoring", "Martin Fowler",
         "Improving the design of existing code."),
        ("Structure and Interpretation of Computer Programs", "Abelson, Sussman",
         "Classic text on the principles of computation."),
        ("Code Complete", "Steve McConnell",
         "A practical handbook of software construction."),
        ("The Mythical Man-Month", "Frederick P. Brooks Jr.",
         "Essays on software engineering management."),
        ("Compilers: Principles, Techniques, and Tools", "Aho, Sethi, Ullman",
         "The dragon book on compiler design."),
        ("Operating System Concepts", "Silberschatz, Galvin, Gagne",
         "Foundations of operating system theory."),
        ("Computer Networks", "Andrew S. Tanenbaum",
         "Comprehensive guide to computer networking."),
        ("Artificial Intelligence: A Modern Approach", "Russell, Norvig",
         "Leading textbook on artificial intelligence."),
        ("Database System Concepts", "Silberschatz, Korth, Sudarshan",
         "Fundamentals of database management systems."),
        ("The C Programming Language", "Kernighan, Ritchie",
         "The definitive reference for the C language."),
    ]

    for title, author, desc in sample_books:
        book = Book(title=title, author=author, description=desc,
                    added_by=admin_user.id, is_public=True)
        db.session.add(book)

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5003)
