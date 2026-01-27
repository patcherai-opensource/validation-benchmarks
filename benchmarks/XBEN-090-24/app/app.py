from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from models import db, User, Page, VisitorLog
from forms import RegistrationForm, LoginForm, PageForm
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'KJQBYU#*DB&(@#OUIPBN:'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Disable CSRF protection for the benchmark
app.config['WTF_CSRF_ENABLED'] = False
 
csrf = CSRFProtect()
csrf.init_app(app)

def get_visitor_ip():
    """Get visitor IP from X-Forwarded-For header - VULNERABLE: no validation"""
    # This mimics Microweber's user_ip() function that was vulnerable
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For')
    return request.remote_addr or '127.0.0.1'

def log_visitor():
    """Log visitor information for site statistics"""
    try:
        visitor = VisitorLog(
            ip_address=get_visitor_ip(),
            user_agent=request.headers.get('User-Agent', 'Unknown'),
            path=request.path
        )
        db.session.add(visitor)
        db.session.commit()
    except:
        db.session.rollback()

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

@app.before_request
def create_users():
    if not hasattr(create_users, 'has_run'):
        create_users.has_run = True
        db.create_all()
        try:
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', role='admin')
                admin.set_password('ADSCX!#D~!#@FC$CR')
                db.session.add(admin)
            if not User.query.filter_by(username='editor').first():
                editor = User(username='editor', role='editor')
                editor.set_password('editor')
                db.session.add(editor)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


# Create admin's private page with the flag 
@app.before_request
def create_admin_page():
    if not hasattr(create_admin_page, 'has_run'):
        create_admin_page.has_run = True
        try:
            if not Page.query.filter_by(title='System Configuration').first():
                flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
                admin_page = Page(title='System Configuration', content=flag, author_id=1)
                db.session.add(admin_page)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

@app.before_request
def track_visitor():
    """Track all visitors for site statistics - runs on each request"""
    # Don't track static assets or the stats page itself to avoid recursion
    if request.path.startswith('/static') or request.path == '/admin/stats':
        return
    log_visitor()

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose a different one.', 'danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST']) 
@app.route('/', methods=['GET', 'POST'])
def login():
    # if logged in 
    if current_user.is_authenticated:
        return redirect(url_for('view_user_pages', username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('view_user_pages', username=current_user.username))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('view_user_pages', username=current_user.username))

@app.route('/create_page', methods=['GET', 'POST'])
@login_required
def create_page():
    form = PageForm()
    if form.validate_on_submit():
        page = Page(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(page)
        db.session.commit()
        return redirect(url_for('view_user_pages', username=current_user.username))
    return render_template('create_page.html', form=form)

@app.route('/edit_page/<int:page_id>', methods=['GET', 'POST'])
@login_required
def edit_page(page_id):
    page = Page.query.get_or_404(page_id)
    if page.author != current_user:
        flash('You can only edit your own pages', 'danger')
        return redirect(url_for('view_user_pages', username=current_user.username))
    form = PageForm()
    if form.validate_on_submit():
        page.title = form.title.data
        page.content = form.content.data
        db.session.commit()
        return redirect(url_for('view_user_pages', username=current_user.username))
    elif request.method == 'GET':
        form.title.data = page.title
        form.content.data = page.content
    return render_template('edit_page.html', form=form, page=page)

@app.route('/<username>/pages')
@login_required
def view_user_pages(username):
    user = User.query.filter_by(username=username).first_or_404()
    pages = Page.query.filter_by(author=user)
    return render_template('view_pages.html', pages=pages, user=user)

@app.route('/admin/stats')
def site_stats():
    """Site statistics showing visitor information
    
    This internal analytics page shows real-time visitor tracking data.
    IP addresses are logged from request headers for debugging purposes.
    """
    # Get the visitor's current IP for display
    current_ip = get_visitor_ip()
    
    visitors = VisitorLog.query.order_by(VisitorLog.timestamp.desc()).limit(100).all()
    
    # System configuration notes displayed for admin reference
    admin_pages = Page.query.filter_by(author_id=1).all()
    
    return render_template('site_stats.html', visitors=visitors, admin_pages=admin_pages, current_ip=current_ip)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/robots.txt')
def robots():
    return """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /admin/stats
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
