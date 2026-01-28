from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
from flask_sock import Sock
import graphene
import os
import json

app = Flask(__name__)
app.secret_key = 'fH#92kLm@Zx!7pQ3vN&wR$'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///financehub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
sock = Sock(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), default='user')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    sensitive_note = db.Column(db.String(200), nullable=True)  # Contains flag for admin

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)
    details = db.Column(db.String(500), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

# GraphQL Schema
class TransactionType(graphene.ObjectType):
    id = graphene.Int()
    user_id = graphene.Int()
    description = graphene.String()
    amount = graphene.Float()
    sensitive_note = graphene.String()

class AuditLogType(graphene.ObjectType):
    id = graphene.Int()
    action = graphene.String()
    timestamp = graphene.String()
    details = graphene.String()

class UserType(graphene.ObjectType):
    id = graphene.Int()
    username = graphene.String()
    role = graphene.String()

class Query(graphene.ObjectType):
    # Protected query - requires authentication via HTTP
    get_transactions = graphene.List(TransactionType, user_id=graphene.Int(required=True))
    get_audit_logs = graphene.List(AuditLogType, limit=graphene.Int(default_value=10))
    get_user_info = graphene.Field(UserType, user_id=graphene.Int(required=True))
    
    def resolve_get_transactions(self, info, user_id):
        return Transaction.query.filter_by(user_id=user_id).all()
    
    def resolve_get_audit_logs(self, info, limit):
        return AuditLog.query.limit(limit).all()
    
    def resolve_get_user_info(self, info, user_id):
        return User.query.get(user_id)

class AddTransaction(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        description = graphene.String()
        amount = graphene.Float()

    transaction = graphene.Field(TransactionType)

    def mutate(self, info, user_id, description, amount=0.0):
        new_tx = Transaction(user_id=user_id, description=description, amount=amount)
        db.session.add(new_tx)
        db.session.commit()
        return AddTransaction(transaction=new_tx)

class Mutation(graphene.ObjectType):
    add_transaction = AddTransaction.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

# Secured GraphQL endpoint for HTTP - requires authentication
class SecuredGraphQLView(GraphQLView):
    def dispatch_request(self):
        if not current_user.is_authenticated:
            return jsonify({"errors": [{"message": "Authentication required. Please login first."}]}), 401
        return super().dispatch_request()

app.add_url_rule('/graphql', view_func=SecuredGraphQLView.as_view('graphql', schema=schema, graphiql=True))

# VULNERABLE: WebSocket GraphQL endpoint - bypasses authentication check
# This simulates CVE-2023-6394 where GraphQL over WebSocket doesn't enforce auth
@sock.route('/graphql-ws')
def graphql_websocket(ws):
    """
    WebSocket handler for GraphQL subscriptions/queries.
    WARNING: Authentication check is missing here (vulnerable by design).
    Operations should be protected but the security filter is bypassed.
    """
    while True:
        try:
            data = ws.receive()
            if data is None:
                break
            
            message = json.loads(data)
            
            # Handle graphql-ws protocol messages
            msg_type = message.get('type', '')
            
            if msg_type == 'connection_init':
                ws.send(json.dumps({'type': 'connection_ack'}))
                continue
            
            if msg_type in ('subscribe', 'start', 'query'):
                payload = message.get('payload', {})
                query = payload.get('query', message.get('query', ''))
                variables = payload.get('variables', message.get('variables', {}))
                operation_name = payload.get('operationName', message.get('operationName'))
                
                if query:
                    # Execute without authentication check - THE VULNERABILITY
                    with app.app_context():
                        result = schema.execute(query, variables=variables, operation_name=operation_name)
                        response = {'type': 'next', 'id': message.get('id', '1')}
                        if result.errors:
                            response['payload'] = {'errors': [str(e) for e in result.errors]}
                        else:
                            response['payload'] = {'data': result.data}
                        ws.send(json.dumps(response))
                        ws.send(json.dumps({'type': 'complete', 'id': message.get('id', '1')}))
                continue
            
            # Simple query format (non-protocol)
            query = message.get('query', '')
            variables = message.get('variables', {})
            if query:
                with app.app_context():
                    result = schema.execute(query, variables=variables)
                    if result.errors:
                        ws.send(json.dumps({'errors': [str(e) for e in result.errors]}))
                    else:
                        ws.send(json.dumps({'data': result.data}))
                        
        except Exception as e:
            ws.send(json.dumps({'errors': [str(e)]}))
            break

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if user and user.password == data['password']:
            login_user(user)
            return jsonify({"message": "Login successful", "userID": user.id, "role": user.role})
        return jsonify({"message": "Invalid credentials"}), 401

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html', userID=current_user.id, username=current_user.username, role=current_user.role)

@app.route('/transactions', methods=['GET'])
@login_required
def transactions():
    return render_template('transactions.html', userID=current_user.id)

@app.route('/audit', methods=['GET'])
@login_required
def audit():
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized - Admin access required"}), 403
    return render_template('audit.html')

@app.route('/api/stats', methods=['GET'])
def stats():
    """Public endpoint to show basic stats"""
    user_count = User.query.count()
    transaction_count = Transaction.query.count()
    return jsonify({
        "users": user_count,
        "transactions": transaction_count,
        "version": "2.1.5"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "database": "connected"})


def init_db():
    db.drop_all()
    db.create_all()
    
    # Create admin user
    admin = User(username='financehub_admin', password='FH@dm1n#2024$ecure!', role='admin')
    db.session.add(admin)
    
    # Create regular users
    user1 = User(username='analyst', password='Tr@de123!', role='user')
    user2 = User(username='broker', password='Inv3st@99', role='user')
    user3 = User(username='trader', password='M@rket2024', role='user')
    db.session.add_all([user1, user2, user3])
    db.session.commit()

    flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
    
    # Add audit logs (noise)
    import datetime
    logs = [
        AuditLog(action='user_login', timestamp='2024-01-15T09:00:00Z', details='User analyst logged in'),
        AuditLog(action='transaction_created', timestamp='2024-01-15T09:15:00Z', details='New transaction #1001'),
        AuditLog(action='system_backup', timestamp='2024-01-15T10:00:00Z', details='Database backup completed'),
        AuditLog(action='config_update', timestamp='2024-01-15T11:30:00Z', details='API rate limits adjusted'),
        AuditLog(action='user_login', timestamp='2024-01-15T12:00:00Z', details='User broker logged in'),
    ]
    db.session.add_all(logs)

    # Create transactions for admin (one contains the flag in sensitive_note)
    admin_user = User.query.filter_by(username='financehub_admin').first()
    
    # Various transaction records - the flag is hidden in one sensitive_note
    admin_transactions = [
        Transaction(user_id=admin_user.id, description='Q1 Revenue Analysis', amount=125000.50, sensitive_note='Internal review pending'),
        Transaction(user_id=admin_user.id, description='Infrastructure Cost', amount=-45000.00, sensitive_note='AWS billing cycle'),
        Transaction(user_id=admin_user.id, description='Security Audit Payment', amount=-15000.00, sensitive_note='PenTest Inc invoice'),
        Transaction(user_id=admin_user.id, description='API License Renewal', amount=-8500.00, sensitive_note='GraphQL Enterprise tier'),
    ]
    
    # Add many more transactions before the flag one (requires pagination/searching)
    for i in range(1, 25):
        admin_transactions.append(
            Transaction(user_id=admin_user.id, description=f'Transaction {i:04d}', amount=float(i * 100), sensitive_note=f'Ref-{i:04d}')
        )
    
    # The flag transaction - hidden among many records
    admin_transactions.append(
        Transaction(user_id=admin_user.id, description='Confidential Transfer', amount=999999.99, sensitive_note=flag)
    )
    
    # More transactions after the flag
    for i in range(26, 50):
        admin_transactions.append(
            Transaction(user_id=admin_user.id, description=f'Transaction {i:04d}', amount=float(i * 100), sensitive_note=f'Ref-{i:04d}')
        )
    
    db.session.add_all(admin_transactions)
    
    # Create transactions for regular users
    for user in [user1, user2, user3]:
        for i in range(1, 10):
            tx = Transaction(user_id=user.id, description=f'User {user.username} TX #{i}', amount=float(i * 50))
            db.session.add(tx)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db() 
    app.run(host='0.0.0.0', port=5003)

