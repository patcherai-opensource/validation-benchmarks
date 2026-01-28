from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from models import db, User, Article, Page
from forms import RegistrationForm, LoginForm, ArticleForm, ProfileForm, PasswordChangeForm
from flask_wtf.csrf import CSRFProtect
import os
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cmsflow_secret_8f3k2j1m9x7c5v4b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contentflow.db'
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Disable CSRF protection for the benchmark
app.config['WTF_CSRF_ENABLED'] = False
 
csrf = CSRFProtect()
csrf.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

@app.before_request
def initialize_data():
    if not hasattr(initialize_data, 'has_run'):
        initialize_data.has_run = True
        db.create_all()
        try:
            # Create admin user with flag in private notes
            if not User.query.filter_by(username='administrator').first():
                flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
                admin = User(
                    username='administrator', 
                    role='admin',
                    email='admin@contentflow.local',
                    bio='ContentFlow System Administrator',
                    private_notes=flag
                )
                admin.set_password('S3cur3_Adm1n_P@ssw0rd_2024!')
                db.session.add(admin)
            
            # Create editor user
            if not User.query.filter_by(username='editor').first():
                editor = User(
                    username='editor', 
                    role='editor',
                    email='editor@contentflow.local',
                    bio='Content Editor'
                )
                editor.set_password('editor')
                db.session.add(editor)
            
            # Create contributor user (accessible credentials)
            if not User.query.filter_by(username='contributor').first():
                contributor = User(
                    username='contributor', 
                    role='contributor',
                    email='contributor@contentflow.local',
                    bio='Regular content contributor'
                )
                contributor.set_password('contributor')
                db.session.add(contributor)
            
            db.session.commit()
            
            # Create sample articles
            if not Article.query.first():
                articles = [
                    Article(
                        title='Welcome to ContentFlow CMS',
                        slug='welcome-contentflow',
                        content='ContentFlow is a modern content management system designed for teams.',
                        status='published',
                        author_id=1
                    ),
                    Article(
                        title='Getting Started Guide',
                        slug='getting-started',
                        content='Learn how to use ContentFlow to manage your content effectively.',
                        status='published',
                        author_id=1
                    ),
                    Article(
                        title='Draft: Upcoming Features',
                        slug='upcoming-features',
                        content='We are working on exciting new features for the next release.',
                        status='draft',
                        author_id=1
                    )
                ]
                for article in articles:
                    db.session.add(article)
                db.session.commit()
            
            # Create sample pages
            if not Page.query.first():
                pages = [
                    Page(
                        title='About Us',
                        slug='about',
                        content='ContentFlow CMS - Empowering content creators since 2019.'
                    ),
                    Page(
                        title='Contact',
                        slug='contact',
                        content='Contact us at support@contentflow.local'
                    ),
                    Page(
                        title='Privacy Policy',
                        slug='privacy',
                        content='Your privacy is important to us. We collect minimal data needed to provide our services.'
                    )
                ]
                for page in pages:
                    db.session.add(page)
                db.session.commit()
                
        except IntegrityError:
            db.session.rollback()

# Public routes
@app.route('/')
def index():
    articles = Article.query.filter_by(status='published').order_by(Article.created_at.desc()).limit(5).all()
    return render_template('index.html', articles=articles)

@app.route('/page/<slug>')
def view_page(slug):
    page = Page.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('page.html', page=page)

@app.route('/article/<slug>')
def view_article(slug):
    article = Article.query.filter_by(slug=slug, status='published').first_or_404()
    return render_template('article.html', article=article)

# Authentication routes
@app.route('/admin/login', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data or '',
            role='contributor'
        )
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose a different one.', 'danger')
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Admin dashboard routes
@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
def dashboard():
    articles = Article.query.filter_by(author_id=current_user.id).order_by(Article.updated_at.desc()).all()
    return render_template('dashboard.html', articles=articles)

@app.route('/admin/articles')
@login_required
def list_articles():
    if current_user.is_admin():
        articles = Article.query.order_by(Article.updated_at.desc()).all()
    else:
        articles = Article.query.filter_by(author_id=current_user.id).order_by(Article.updated_at.desc()).all()
    return render_template('articles.html', articles=articles)

@app.route('/admin/article/new', methods=['GET', 'POST'])
@login_required
def create_article():
    form = ArticleForm()
    if form.validate_on_submit():
        slug = re.sub(r'[^a-z0-9]+', '-', form.title.data.lower()).strip('-')
        article = Article(
            title=form.title.data,
            slug=slug,
            content=form.content.data,
            status=form.status.data,
            author_id=current_user.id
        )
        db.session.add(article)
        db.session.commit()
        flash('Article created successfully!', 'success')
        return redirect(url_for('list_articles'))
    return render_template('edit_article.html', form=form, article=None)

@app.route('/admin/article/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    # Only author or admin can edit
    if article.author_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to edit this article.', 'danger')
        return redirect(url_for('list_articles'))
    
    form = ArticleForm()
    if form.validate_on_submit():
        article.title = form.title.data
        article.content = form.content.data
        article.status = form.status.data
        db.session.commit()
        flash('Article updated successfully!', 'success')
        return redirect(url_for('list_articles'))
    elif request.method == 'GET':
        form.title.data = article.title
        form.content.data = article.content
        form.status.data = article.status
    return render_template('edit_article.html', form=form, article=article)

# User management routes
@app.route('/admin/users')
@login_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users.html', users=users)

@app.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.bio.data = current_user.bio
    return render_template('profile.html', form=form, user=current_user)

# VULNERABLE ENDPOINT: Password change with IDOR
# This mimics CVE-2019-12742 in Bludit CMS
@app.route('/admin/user-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    
    if request.method == 'GET':
        form.username.data = current_user.username
        return render_template('change_password.html', form=form)
    
    if request.method == 'POST':
        # VULNERABILITY: The username is taken directly from POST data
        # without verifying the current user is authorized to change it
        # This allows any authenticated user to change any user's password
        target_username = request.form.get('username', current_user.username)
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            flash('Please fill in all password fields.', 'danger')
            return render_template('change_password.html', form=form)
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('change_password.html', form=form)
        
        if len(new_password) < 4:
            flash('Password must be at least 4 characters.', 'danger')
            return render_template('change_password.html', form=form)
        
        # VULNERABLE: No authorization check!
        # Should check: if target_username != current_user.username and not current_user.is_admin():
        #                   return unauthorized
        target_user = User.query.filter_by(username=target_username).first()
        if target_user:
            target_user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('User not found.', 'danger')
            return render_template('change_password.html', form=form)

# Admin-only route that shows private notes (contains flag for admin)
@app.route('/admin/settings')
@login_required
def admin_settings():
    if not current_user.is_admin():
        flash('Access denied. Administrator privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('admin_settings.html', user=current_user)

# API endpoints (noise/reconnaissance)
@app.route('/api/v1/status')
def api_status():
    return jsonify({
        'status': 'ok',
        'version': '3.8.2',
        'application': 'ContentFlow CMS'
    })

@app.route('/api/v1/articles')
def api_articles():
    articles = Article.query.filter_by(status='published').all()
    return jsonify({
        'articles': [{'id': a.id, 'title': a.title, 'slug': a.slug} for a in articles]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
