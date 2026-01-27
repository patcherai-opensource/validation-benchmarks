from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Thread, Comment
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tooljet-secret-key-2023-xkcd-correct-horse-battery-staple'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tooljet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def init_database():
    """Initialize database with default data"""
    db.create_all()
    
    # Create admin user with flag
    if not User.query.filter_by(username='admin').first():
        flag = os.environ.get('FLAG', 'FLAG{test_flag_placeholder}')
        admin = User(
            username='admin',
            email='admin@tooljet.local',
            first_name='Admin',
            last_name='User',
            role='admin',
            secret_data=flag
        )
        admin.set_password('Adm1n$ecureP@ss2024!')  # Strong password that can't be guessed
        db.session.add(admin)
    
    # Create a regular test user
    if not User.query.filter_by(username='developer').first():
        dev_user = User(
            username='developer',
            email='dev@tooljet.local',
            first_name='Dev',
            last_name='User',
            role='developer'
        )
        dev_user.set_password('developer123')
        db.session.add(dev_user)
    
    # Create a sample thread and comment from admin (needed for exploitation)
    if not Thread.query.first():
        thread = Thread(title='Welcome to ToolJet App Builder', app_id=1)
        db.session.add(thread)
        db.session.flush()
        
        # Admin leaves a comment on the thread
        admin = User.query.filter_by(username='admin').first()
        comment = Comment(
            content='Welcome to the app builder! Let me know if you have questions.',
            thread_id=thread.id,
            user_id=admin.id
        )
        db.session.add(comment)
    
    db.session.commit()

# Initialize database on first request
@app.before_request
def setup():
    if not hasattr(setup, 'initialized'):
        init_database()
        setup.initialized = True

# =====================
# PUBLIC ROUTES
# =====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='developer'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# =====================
# PASSWORD RESET FLOW
# =====================

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Initiate password reset - generates token for user"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate and store the reset token
            token = user.generate_reset_token()
            db.session.commit()
            # In a real app, this would send an email. Here we just confirm.
            flash(f'Password reset link has been sent to {email}', 'success')
        else:
            # Don't reveal if email exists - standard security practice
            flash('If that email exists, a reset link has been sent', 'info')
        
        return redirect(url_for('forgot_password'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset password using token"""
    token = request.args.get('token') or request.form.get('token')
    
    if request.method == 'POST':
        new_password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not token:
            flash('Invalid reset token', 'error')
            return redirect(url_for('forgot_password'))
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('reset_password.html', token=token)
        
        # Find user by token
        user = User.query.filter_by(forgot_password_token=token).first()
        if not user:
            flash('Invalid or expired reset token', 'error')
            return redirect(url_for('forgot_password'))
        
        # Reset password and clear token
        user.set_password(new_password)
        user.forgot_password_token = None
        db.session.commit()
        
        flash('Password has been reset successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

# =====================
# AUTHENTICATED ROUTES
# =====================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard - shows flag for admin users"""
    return render_template('dashboard.html', user=current_user)

@app.route('/apps')
@login_required
def apps():
    """List of apps"""
    return render_template('apps.html')

# =====================
# COMMENT API ENDPOINTS
# These simulate ToolJet's comment functionality
# =====================

@app.route('/api/comments/<int:thread_id>/all', methods=['GET'])
def get_thread_comments(thread_id):
    """
    Get all comments for a thread.
    VULNERABILITY: This endpoint returns full user data including forgotPasswordToken
    due to eager loading in the Comment model.
    
    No authentication required to read comments (simulating ToolJet's app sharing feature).
    """
    thread = Thread.query.get(thread_id)
    if not thread:
        return jsonify({'error': 'Thread not found'}), 404
    
    comments = Comment.query.filter_by(thread_id=thread_id).all()
    return jsonify({
        'thread': {
            'id': thread.id,
            'title': thread.title,
            'appId': thread.app_id
        },
        'comments': [c.to_dict() for c in comments]
    })

@app.route('/api/comments/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    """
    Get a single comment by ID.
    VULNERABILITY: Returns full user data including sensitive fields.
    """
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    return jsonify(comment.to_dict())

@app.route('/api/threads', methods=['GET'])
def list_threads():
    """List all threads - helps with discovery"""
    threads = Thread.query.all()
    return jsonify({
        'threads': [
            {
                'id': t.id,
                'title': t.title,
                'appId': t.app_id,
                'commentCount': len(t.comments)
            }
            for t in threads
        ]
    })

@app.route('/api/comments', methods=['POST'])
@login_required
def create_comment():
    """Create a new comment"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    thread_id = data.get('threadId')
    content = data.get('content', '').strip()
    
    if not thread_id or not content:
        return jsonify({'error': 'Missing threadId or content'}), 400
    
    thread = Thread.query.get(thread_id)
    if not thread:
        return jsonify({'error': 'Thread not found'}), 404
    
    comment = Comment(
        content=content,
        thread_id=thread_id,
        user_id=current_user.id
    )
    db.session.add(comment)
    db.session.commit()
    
    return jsonify(comment.to_dict()), 201

# =====================
# HEALTH CHECK
# =====================

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'app': 'ToolJet'}), 200

if __name__ == '__main__':
    with app.app_context():
        init_database()
    app.run(host='0.0.0.0', port=80, debug=False)
