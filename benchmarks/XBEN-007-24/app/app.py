from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
import graphene
import os
import re

app = Flask(__name__)
app.secret_key = '@#$%^R&GYUIUBJIU#@*DF&G*H'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///irrd.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Supported password hash types - used for sanitization
# BUG: The sanitization only matches UPPERCASE algorithm names, but the database
# may contain lowercase or mixed-case algorithm names which bypass the filter
PASSWORD_HASHERS = {
    'MD5-PW': 'MD5 Password Hash',
    'CRYPT-PW': 'Crypt Password Hash',
    'BCRYPT-PW': 'BCrypt Password Hash',
}

def remove_auth_hashes(text):
    """
    Remove password hashes from text to prevent credential leakage.
    
    VULNERABILITY: This function only matches algorithm names that appear
    in PASSWORD_HASHERS dictionary (which are UPPERCASE). If the algorithm
    name in the text is lowercase or mixed-case (e.g., 'md5-pw:' instead of
    'MD5-PW:'), the hash will NOT be removed, leaking sensitive data.
    
    This mimics CVE behavior in IRRd where case-insensitive matching was
    not used, allowing password hash leakage through the GraphQL API.
    """
    result = text
    for hasher_name in PASSWORD_HASHERS.keys():
        # BUG: Only matches exact case - lowercase variants bypass this filter
        pattern = re.compile(r'auth:\s*' + re.escape(hasher_name) + r'\s+\S+', re.MULTILINE)
        result = pattern.sub('auth: [FILTERED]', result)
    return result


# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


class Maintainer(db.Model):
    """
    RPSL Maintainer object - similar to IRRd mntner objects.
    Contains authentication credentials for managing network objects.
    """
    id = db.Column(db.Integer, primary_key=True)
    mnt_name = db.Column(db.String(80), unique=True, nullable=False)
    descr = db.Column(db.String(200), nullable=False)
    admin_c = db.Column(db.String(80), nullable=False)
    # The auth field contains password hashes, should be sanitized before returning
    # Format: "auth: ALGORITHM hash_value"
    auth = db.Column(db.String(500), nullable=False)
    remarks = db.Column(db.String(500), nullable=True)
    source = db.Column(db.String(50), nullable=False, default='EXAMPLE')
    
    def get_object_text(self):
        """Return full RPSL-style object text"""
        lines = [
            f"mntner:      {self.mnt_name}",
            f"descr:       {self.descr}",
            f"admin-c:     {self.admin_c}",
            f"auth:        {self.auth}",
        ]
        if self.remarks:
            lines.append(f"remarks:     {self.remarks}")
        lines.append(f"source:      {self.source}")
        return "\n".join(lines)


@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))


# GraphQL Schema
class MaintainerType(graphene.ObjectType):
    id = graphene.Int()
    mnt_name = graphene.String()
    descr = graphene.String()
    admin_c = graphene.String()
    # The auth field - should be sanitized but has a case-sensitivity bug
    auth = graphene.String()
    remarks = graphene.String()
    source = graphene.String()
    # Full object text representation
    object_text = graphene.String()


class Query(graphene.ObjectType):
    # Query to get RPSL objects (maintainers) - similar to IRRd's rpslObjects query
    rpsl_objects = graphene.List(
        MaintainerType, 
        rpsl_pk=graphene.String(required=False),
        source=graphene.String(required=False)
    )
    
    # Get all maintainers
    maintainers = graphene.List(MaintainerType)
    
    def resolve_rpsl_objects(self, info, rpsl_pk=None, source=None):
        """
        Query RPSL objects (maintainers) from the database.
        
        This resolver attempts to sanitize password hashes before returning,
        but the sanitization has a case-sensitivity vulnerability.
        """
        query = Maintainer.query
        
        if rpsl_pk:
            query = query.filter_by(mnt_name=rpsl_pk)
        if source:
            query = query.filter_by(source=source)
            
        maintainers = query.all()
        
        result = []
        for mnt in maintainers:
            # Sanitize auth field - but this has a case-sensitivity bug!
            sanitized_auth = remove_auth_hashes(f"auth: {mnt.auth}")
            # Extract just the auth value from the sanitized line
            if '[FILTERED]' in sanitized_auth:
                auth_value = '[FILTERED]'
            else:
                auth_value = mnt.auth  # BUG: Hash leaks if case doesn't match
            
            # Also sanitize object_text
            sanitized_object_text = remove_auth_hashes(mnt.get_object_text())
            
            result.append(MaintainerType(
                id=mnt.id,
                mnt_name=mnt.mnt_name,
                descr=mnt.descr,
                admin_c=mnt.admin_c,
                auth=auth_value,
                remarks=mnt.remarks,
                source=mnt.source,
                object_text=sanitized_object_text
            ))
        
        return result
    
    def resolve_maintainers(self, info):
        """List all maintainers with sanitized auth fields."""
        return self.resolve_rpsl_objects(info)


schema = graphene.Schema(query=Query)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if user and user.password == data['password']:
            login_user(user)
            return jsonify({"message": "Login successful", "userID": user.id})
        return jsonify({"message": "Invalid credentials"}), 401

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/api/maintainers')
def list_maintainers():
    """REST API endpoint to list maintainer names (for discovery)."""
    maintainers = Maintainer.query.all()
    return jsonify([{"mnt_name": m.mnt_name, "descr": m.descr} for m in maintainers])


def init_db():
    db.drop_all()
    db.create_all()
    
    # Add admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='irrd_admin_2024')
        db.session.add(admin)
        db.session.commit()

    # Add regular user for testing
    if not User.query.filter_by(username='operator').first():
        operator = User(username='operator', password='operator')
        db.session.add(operator)
        db.session.commit()

    # Get the flag from environment (injected at build time)
    flag = os.getenv('FLAG', 'FLAG{test_flag_placeholder}')

    # Create maintainer objects with various auth formats
    # Some use UPPERCASE (properly sanitized), some use lowercase (VULNERABLE!)
    
    if Maintainer.query.count() == 0:
        # Maintainer with UPPERCASE auth - will be properly sanitized
        mnt1 = Maintainer(
            mnt_name='EXAMPLE-MNT',
            descr='Example Maintainer Object',
            admin_c='ADMIN-EXAMPLE',
            auth='MD5-PW $1$saltsalt$hashedpassword123',
            remarks='This maintainer uses standard uppercase auth format',
            source='EXAMPLE'
        )
        db.session.add(mnt1)
        
        # Maintainer with UPPERCASE BCRYPT - will be properly sanitized
        mnt2 = Maintainer(
            mnt_name='SECURE-MNT',
            descr='Secure Maintainer with BCrypt',
            admin_c='ADMIN-SECURE',
            auth='BCRYPT-PW $2b$12$hashedpassword456',
            remarks='Uses strong BCrypt hashing',
            source='EXAMPLE'
        )
        db.session.add(mnt2)
        
        # VULNERABLE: Maintainer with lowercase auth - bypasses sanitization!
        # The flag is hidden in this "password hash" which will be leaked
        # because 'md5-pw' (lowercase) doesn't match 'MD5-PW' (uppercase) in the filter
        mnt3 = Maintainer(
            mnt_name='LEGACY-MNT',
            descr='Legacy Maintainer with old config format',
            admin_c='ADMIN-LEGACY',
            auth=f'md5-pw {flag}',  # lowercase 'md5-pw' bypasses the filter!
            remarks='Uses legacy lowercase auth format for compatibility',
            source='EXAMPLE'
        )
        db.session.add(mnt3)
        
        # Another maintainer with mixed case - also vulnerable
        mnt4 = Maintainer(
            mnt_name='MIXED-MNT',
            descr='Mixed case auth example',
            admin_c='ADMIN-MIXED',
            auth='Md5-Pw $1$mixed$casebypass',
            remarks='Mixed case auth format',
            source='EXAMPLE'
        )
        db.session.add(mnt4)
        
        # Maintainer with CRYPT-PW (uppercase) - properly sanitized
        mnt5 = Maintainer(
            mnt_name='CRYPT-MNT',
            descr='Crypt password maintainer',
            admin_c='ADMIN-CRYPT',
            auth='CRYPT-PW abcdefghij',
            remarks='Uses crypt hashing',
            source='EXAMPLE'
        )
        db.session.add(mnt5)
        
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        init_db() 
    app.run(host='0.0.0.0', port=5003)

