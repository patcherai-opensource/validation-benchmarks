import os
import re
import string
import random
import logging
from functools import wraps

from flask import (Flask, request, jsonify, render_template, redirect,
                   url_for, flash, abort)
from flask_login import (LoginManager, UserMixin, login_user, logout_user,
                         current_user, login_required)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calibreweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('calibre-web')


# ---------- Configuration model ----------
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    config_public_reg = db.Column(db.Boolean, default=True)
    config_password_min_length = db.Column(db.Integer, default=1)
    config_password_number = db.Column(db.Boolean, default=False)
    config_password_lower = db.Column(db.Boolean, default=False)
    config_password_upper = db.Column(db.Boolean, default=False)
    config_password_special = db.Column(db.Boolean, default=False)
    mail_server = db.Column(db.String(128), default='localhost')
    mail_port = db.Column(db.Integer, default=25)
    config_calibre_dir = db.Column(db.String(512), default='/books')
    config_uploading = db.Column(db.Boolean, default=False)
    config_anonbrowse = db.Column(db.Boolean, default=False)
    config_keyfile = db.Column(db.String(512), default='')
    config_certfile = db.Column(db.String(512), default='')
    config_server_url = db.Column(db.String(512), default='')
    config_ldap_provider_url = db.Column(db.String(512), default='')
    config_ldap_authentication = db.Column(db.Boolean, default=False)
    config_kepubifypath = db.Column(db.String(512), default='')
    config_converterpath = db.Column(db.String(512), default='')
    config_access_token = db.Column(db.String(512), default='')


def get_config():
    return Settings.query.first()


# ---------- Database Models ----------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Integer, default=0)  # 0 = user, 1 = admin
    locale = db.Column(db.String(10), default='en')
    default_language = db.Column(db.String(10), default='all')

    @property
    def is_admin(self):
        return self.role == 1


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    author = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, default='')
    language = db.Column(db.String(10), default='en')
    rating = db.Column(db.Integer, default=0)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))


class Shelf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)


class ShelfBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shelf_id = db.Column(db.Integer, db.ForeignKey('shelf.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------- Password validation ----------
def valid_password(password):
    """Validate password against configured policy.
    Used in profile password change and admin user management."""
    cfg = get_config()
    if cfg is None:
        return True
    if len(password) < cfg.config_password_min_length:
        return False
    if cfg.config_password_number and not re.search(r'\d', password):
        return False
    if cfg.config_password_lower and not re.search(r'[a-z]', password):
        return False
    if cfg.config_password_upper and not re.search(r'[A-Z]', password):
        return False
    if cfg.config_password_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True


def generate_random_password(min_length):
    """Generate a random password for registration (email flow).
    NOTE: Only uses lowercase letters based on min_length config."""
    length = max(min_length, 1)
    chars = string.ascii_lowercase
    return ''.join(random.choice(chars) for _ in range(length))


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ---------- Error handlers ----------
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', message='Access denied.'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='Page not found.'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', message='An internal error occurred.'), 500


# ---------- Public routes ----------
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('books'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('books'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            log.info("User '%s' logged in", username)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('books'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    cfg = get_config()
    if cfg is None or not cfg.config_public_reg:
        flash('Public registration is disabled.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not email:
            flash('Username and email are required.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')

        # VULNERABILITY: registration does NOT call valid_password()
        # Password is accepted as-is if provided, or generated with weak defaults
        if not password:
            password = generate_random_password(cfg.config_password_min_length)

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=0
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. Please log in.', 'success')
        log.info("New user registered: %s", username)
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ---------- Book browsing ----------
@app.route('/books')
@login_required
def books():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('q', '').strip()
    query = Book.query
    if search:
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%')
            )
        )
    pagination = query.order_by(Book.title).paginate(
        page=page, per_page=per_page, error_out=False)
    return render_template('books.html', books=pagination.items,
                           pagination=pagination, search=search)


@app.route('/book/<int:book_id>')
@login_required
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)


# ---------- User profile ----------
@app.route('/me', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        locale = request.form.get('locale', 'en')
        if email:
            current_user.email = email
        current_user.locale = locale
        db.session.commit()
        flash('Profile updated.', 'success')
    return render_template('profile.html', user=current_user)


@app.route('/me/password', methods=['POST'])
@login_required
def change_password():
    old_pw = request.form.get('old_password', '')
    new_pw = request.form.get('new_password', '')
    confirm_pw = request.form.get('confirm_password', '')

    if not check_password_hash(current_user.password, old_pw):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('profile'))

    if new_pw != confirm_pw:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('profile'))

    # Password change DOES enforce policy (unlike registration)
    if not valid_password(new_pw):
        cfg = get_config()
        flash(f'Password does not meet requirements: minimum {cfg.config_password_min_length} characters, '
              f'must include {"numbers, " if cfg.config_password_number else ""}'
              f'{"uppercase, " if cfg.config_password_upper else ""}'
              f'{"lowercase, " if cfg.config_password_lower else ""}'
              f'{"special characters" if cfg.config_password_special else ""}',
              'danger')
        return redirect(url_for('profile'))

    current_user.password = generate_password_hash(new_pw)
    db.session.commit()
    flash('Password changed successfully.', 'success')
    return redirect(url_for('profile'))


# ---------- Shelves ----------
@app.route('/shelf/create', methods=['POST'])
@login_required
def create_shelf():
    name = request.form.get('name', '').strip()
    is_public = request.form.get('is_public') == 'on'
    if name:
        shelf = Shelf(name=name, user_id=current_user.id, is_public=is_public)
        db.session.add(shelf)
        db.session.commit()
        flash('Shelf created.', 'success')
    return redirect(url_for('books'))


# ---------- Admin routes ----------
@app.route('/admin')
@admin_required
def admin_panel():
    users = User.query.all()
    return render_template('admin.html', users=users)


@app.route('/admin/user/<int:user_id>', methods=['POST'])
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    new_pw = request.form.get('password', '').strip()
    role = request.form.get('role', '0')

    if new_pw:
        # Admin user management also enforces password policy
        if not valid_password(new_pw):
            flash('Password does not meet configured policy.', 'danger')
            return redirect(url_for('admin_panel'))
        user.password = generate_password_hash(new_pw)

    user.role = int(role) if role in ('0', '1') else user.role
    db.session.commit()
    flash(f'User {user.username} updated.', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    cfg = get_config()
    if request.method == 'POST':
        cfg.config_public_reg = request.form.get('config_public_reg') == 'on'
        cfg.config_password_min_length = int(request.form.get('config_password_min_length', 1))
        cfg.config_password_number = request.form.get('config_password_number') == 'on'
        cfg.config_password_lower = request.form.get('config_password_lower') == 'on'
        cfg.config_password_upper = request.form.get('config_password_upper') == 'on'
        cfg.config_password_special = request.form.get('config_password_special') == 'on'
        cfg.config_uploading = request.form.get('config_uploading') == 'on'
        cfg.config_anonbrowse = request.form.get('config_anonbrowse') == 'on'
        db.session.commit()
        flash('Settings saved.', 'success')
    return render_template('admin_settings.html', config=cfg)


# ---------- Health endpoint ----------
@app.route('/ping')
def ping():
    return 'ok', 200


# ---------- Database initialization ----------
def read_flag():
    """Read flag from build-time injected file and remove it."""
    flag_path = '/app/flag.txt'
    try:
        with open(flag_path, 'r') as f:
            flag_val = f.read().strip()
        os.remove(flag_path)
        return flag_val
    except FileNotFoundError:
        return 'FLAG{placeholder}'


def init_db():
    db.drop_all()
    db.create_all()

    # Create default settings
    flag = read_flag()
    cfg = Settings(
        config_public_reg=True,
        config_password_min_length=8,
        config_password_number=True,
        config_password_lower=True,
        config_password_upper=True,
        config_password_special=True,
        mail_server='localhost',
        mail_port=25,
        config_calibre_dir='/books',
        config_uploading=False,
        config_anonbrowse=False,
        config_server_url='https://library.calibre.local',
        config_access_token=flag
    )
    db.session.add(cfg)

    # Admin user with a weak password (doesn't meet own policy)
    admin = User(
        username='admin',
        email='admin@calibre.local',
        password=generate_password_hash('admin123'),
        role=1
    )
    db.session.add(admin)
    db.session.commit()

    # Sample regular users
    for i, (uname, email, pw) in enumerate([
        ('librarian', 'librarian@calibre.local', generate_password_hash('Kj$8mNpQ2x!')),
        ('reader', 'reader@calibre.local', generate_password_hash('Bv#4wLsR9y@')),
        ('curator', 'curator@calibre.local', generate_password_hash('Hn&6tZcF3a%')),
    ]):
        u = User(username=uname, email=email, password=pw, role=0)
        db.session.add(u)
    db.session.commit()

    # Sample book catalog
    books_data = [
        ('The Great Gatsby', 'F. Scott Fitzgerald', 'A novel set in the Jazz Age on Long Island.', 'en', 4),
        ('To Kill a Mockingbird', 'Harper Lee', 'A classic novel about racial injustice in the American South.', 'en', 5),
        ('1984', 'George Orwell', 'A dystopian social science fiction novel.', 'en', 5),
        ('Pride and Prejudice', 'Jane Austen', 'A romantic novel of manners.', 'en', 4),
        ('The Catcher in the Rye', 'J.D. Salinger', 'A novel about teenage alienation and loss of innocence.', 'en', 3),
        ('One Hundred Years of Solitude', 'Gabriel Garcia Marquez', 'A landmark of magical realism.', 'es', 5),
        ('Brave New World', 'Aldous Huxley', 'A dystopian novel set in a futuristic World State.', 'en', 4),
        ('The Lord of the Rings', 'J.R.R. Tolkien', 'An epic high-fantasy novel.', 'en', 5),
        ('Crime and Punishment', 'Fyodor Dostoevsky', 'A novel about the mental anguish of a murderer.', 'ru', 5),
        ('Don Quixote', 'Miguel de Cervantes', 'The adventures of a noble wannabe knight.', 'es', 4),
        ('The Brothers Karamazov', 'Fyodor Dostoevsky', 'A philosophical novel about faith, doubt, and morality.', 'ru', 5),
        ('Fahrenheit 451', 'Ray Bradbury', 'A dystopian novel about a future American society.', 'en', 4),
        ('War and Peace', 'Leo Tolstoy', 'A novel chronicling French invasion of Russia.', 'ru', 5),
        ('Animal Farm', 'George Orwell', 'A satirical allegorical novella.', 'en', 4),
        ('The Odyssey', 'Homer', 'An ancient Greek epic poem.', 'el', 5),
        ('Les Miserables', 'Victor Hugo', 'A French historical novel.', 'fr', 5),
        ('Moby-Dick', 'Herman Melville', 'The narrative of Captain Ahab obsessive quest.', 'en', 4),
        ('Wuthering Heights', 'Emily Bronte', 'A wild passionate tale of the intense love.', 'en', 3),
        ('Jane Eyre', 'Charlotte Bronte', 'An autobiography of a strong independent woman.', 'en', 4),
        ('The Divine Comedy', 'Dante Alighieri', 'An Italian narrative poem.', 'it', 5),
    ]

    for title, author, desc, lang, rating in books_data:
        book = Book(title=title, author=author, description=desc,
                    language=lang, rating=rating, added_by=admin.id)
        db.session.add(book)

    db.session.commit()
    log.info("Database initialized with sample data")


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5003)
