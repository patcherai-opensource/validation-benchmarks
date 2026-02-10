from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from models import db, User, Draft
from forms import RegistrationForm, LoginForm, DraftForm, ChangePasswordForm
from flask_wtf.csrf import CSRFProtect
import os
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

app.config['WTF_CSRF_ENABLED'] = False
 
csrf = CSRFProtect()
csrf.init_app(app)

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
                admin.set_password(secrets.token_hex(16))
                db.session.add(admin)
            if not User.query.filter_by(username='user').first():
                user = User(username='user', role='user')
                user.set_password('user')
                db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


@app.before_request
def create_admin_draft():
    if not hasattr(create_admin_draft, 'has_run'):
        create_admin_draft.has_run = True
        try:
            if not Draft.query.filter_by(title='System Configuration Notes').first():
                flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
                admin_draft = Draft(title='System Configuration Notes', content=f'Server maintenance scheduled for next week.\n\nAPI Key: {flag}\n\nRemember to update SSL certificates.', author_id=1)
                db.session.add(admin_draft)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, role='user')
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
        return redirect(url_for('view_user_drafts', username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('view_user_drafts', username=current_user.username))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('view_user_drafts', username=current_user.username))

@app.route('/create_draft', methods=['GET', 'POST'])
@login_required
def create_draft():
    form = DraftForm()
    if form.validate_on_submit():
        draft = Draft(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(draft)
        db.session.commit()
        return redirect(url_for('view_user_drafts', username=current_user.username))
    return render_template('create_draft.html', form=form)

@app.route('/edit_draft/<int:draft_id>', methods=['GET', 'POST'])
@login_required
def edit_draft(draft_id):
    draft = Draft.query.get_or_404(draft_id)
    if draft.author != current_user:
        flash('You do not have permission to edit this draft.', 'danger')
        return redirect(url_for('view_user_drafts', username=current_user.username))
    form = DraftForm()
    if form.validate_on_submit():
        draft.title = form.title.data
        draft.content = form.content.data
        db.session.commit()
        return redirect(url_for('view_user_drafts', username=current_user.username))
    elif request.method == 'GET':
        form.title.data = draft.title
        form.content.data = draft.content
    return render_template('edit_draft.html', form=form, draft=draft)

@app.route('/<username>/drafts')
@login_required
def view_user_drafts(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user != current_user:
        flash('You can only view your own drafts.', 'danger')
        return redirect(url_for('view_user_drafts', username=current_user.username))
    drafts = Draft.query.filter_by(author=user)
    return render_template('view_drafts.html', drafts=drafts, user=user)

@app.route('/account/settings')
@login_required
def account_settings():
    return render_template('account_settings.html', user=current_user)

@app.route('/account/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if request.method == 'POST':
        username = request.form.get('username', current_user.username)
        new_password = request.form.get('newPassword')
        confirm_password = request.form.get('confirmPassword')
        
        if not new_password or not confirm_password:
            flash('Please fill in all fields.', 'danger')
            return render_template('change_password.html', form=form)
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('change_password.html', form=form)
        
        if len(new_password) < 4:
            flash('Password must be at least 4 characters.', 'danger')
            return render_template('change_password.html', form=form)
        
        target_user = User.query.filter_by(username=username).first()
        if not target_user:
            flash('User not found.', 'danger')
            return render_template('change_password.html', form=form)
        
        target_user.set_password(new_password)
        db.session.commit()
        flash('Password changed successfully.', 'success')
        return redirect(url_for('account_settings'))
    
    return render_template('change_password.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error_code=500, message='Internal server error'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
