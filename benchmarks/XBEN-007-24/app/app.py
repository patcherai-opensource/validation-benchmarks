from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
from flask_sock import Sock
import graphene
import os
import json

app = Flask(__name__)
app.secret_key = 'K9#mP$vL2@nQ8wX5!jR7tY0uI6oA3sD'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
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

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    item_details = db.Column(db.String(500), nullable=True)
    secret_notes = db.Column(db.String(200), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

# GraphQL Schema
class InventoryItemType(graphene.ObjectType):
    id = graphene.Int()
    owner_id = graphene.Int()
    item_name = graphene.String()
    item_details = graphene.String()
    secret_notes = graphene.String()

class Query(graphene.ObjectType):
    get_inventory = graphene.List(InventoryItemType, owner_id=graphene.Int(required=True))
    get_all_items = graphene.List(InventoryItemType)

    def resolve_get_inventory(self, info, owner_id):
        return InventoryItem.query.filter_by(owner_id=owner_id).all()
    
    def resolve_get_all_items(self, info):
        # This should only be accessible to admins
        return InventoryItem.query.all()

class AddInventoryItem(graphene.Mutation):
    class Arguments:
        owner_id = graphene.Int(required=True)
        item_name = graphene.String(required=True)
        item_details = graphene.String()

    inventory_item = graphene.Field(InventoryItemType)

    def mutate(self, info, owner_id, item_name, item_details=None):
        new_item = InventoryItem(owner_id=owner_id, item_name=item_name, item_details=item_details)
        db.session.add(new_item)
        db.session.commit()
        return AddInventoryItem(inventory_item=new_item)

class Mutation(graphene.ObjectType):
    add_inventory_item = AddInventoryItem.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

# Protected GraphQL HTTP endpoint - requires authentication
class AuthenticatedGraphQLView(GraphQLView):
    def dispatch_request(self):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required", "message": "Please login to access GraphQL API"}), 401
        return super().dispatch_request()

app.add_url_rule('/graphql', view_func=AuthenticatedGraphQLView.as_view('graphql', schema=schema, graphiql=True))

# WebSocket GraphQL endpoint - VULNERABLE: No authentication check!
# This simulates CVE-2023-6394 where WebSocket GraphQL bypasses auth
@sock.route('/graphql-ws')
def graphql_websocket(ws):
    """
    WebSocket handler for GraphQL subscriptions and queries.
    WARNING: This endpoint does not enforce authentication - operations
    bypass the security layer applied to HTTP requests.
    """
    while True:
        try:
            data = ws.receive()
            if data is None:
                break
            
            message = json.loads(data)
            
            # Handle GraphQL-WS protocol messages
            msg_type = message.get('type', '')
            
            if msg_type == 'connection_init':
                # Accept connection without auth check (VULNERABILITY)
                ws.send(json.dumps({'type': 'connection_ack'}))
            
            elif msg_type in ['start', 'subscribe']:
                # Process GraphQL operation without authentication (VULNERABILITY)
                payload = message.get('payload', {})
                query = payload.get('query', '')
                variables = payload.get('variables', {})
                operation_id = message.get('id', '1')
                
                # Execute the GraphQL query
                result = schema.execute(query, variables=variables)
                
                response_data = {}
                if result.data:
                    response_data['data'] = dict(result.data)
                if result.errors:
                    response_data['errors'] = [str(e) for e in result.errors]
                
                ws.send(json.dumps({
                    'type': 'data',
                    'id': operation_id,
                    'payload': response_data
                }))
                
                # Send complete message
                ws.send(json.dumps({
                    'type': 'complete',
                    'id': operation_id
                }))
            
            elif msg_type == 'stop':
                break
                
        except Exception as e:
            ws.send(json.dumps({
                'type': 'error',
                'payload': {'message': str(e)}
            }))
            break

@app.route('/')
def home():
    return render_template('home.html')

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

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', userID=current_user.id, username=current_user.username)




@app.route('/add_item', methods=['GET'])
@login_required
def add_item():
    return render_template('add_item.html', userID=current_user.id)

@app.route('/view_inventory', methods=['GET'])
@login_required
def view_inventory():
    user = current_user
    return render_template('view_inventory.html', userID=current_user.id, username=user.username)

@app.route('/api/status')
def api_status():
    """API status endpoint showing available endpoints"""
    return jsonify({
        "status": "online",
        "version": "2.1.0",
        "graphql": {
            "http": "/graphql",
            "websocket": "/graphql-ws",
            "note": "HTTP endpoint requires authentication. WebSocket available for real-time subscriptions."
        },
        "authentication": "/login"
    })


def init_db():
    db.drop_all()
    db.create_all()
    
    # Add admin user with strong password
    if not User.query.filter_by(username='warehouse_admin').first():
        admin = User(username='warehouse_admin', password='Wh4r3h0us3!Adm1n#2024', role='admin')
        db.session.add(admin)
        db.session.commit()

    # Add regular employee
    if not User.query.filter_by(username='employee').first():
        employee = User(username='employee', password='emp123', role='user')
        db.session.add(employee)
        db.session.commit()

    # Get the admin user
    admin = User.query.filter_by(username='warehouse_admin').first()
    employee = User.query.filter_by(username='employee').first()

    flag = os.getenv('FLAG', 'FLAG{test_flag_placeholder}')

    # Add inventory items for admin (containing sensitive data)
    if InventoryItem.query.filter_by(owner_id=admin.id).count() == 0:
        # Add various inventory items, one contains the flag in secret_notes
        items = [
            ("Server Rack A1", "Dell PowerEdge R740 - Production Database Server", None),
            ("Server Rack A2", "HP ProLiant DL380 - Application Server", None),
            ("Network Switch B1", "Cisco Catalyst 9300 - Core Switch", None),
            ("Backup System C1", "Synology RS4021xs+ - Critical Backup Storage", flag),
            ("Firewall D1", "Palo Alto PA-5250 - Perimeter Security", None),
            ("UPS Unit E1", "APC Smart-UPS 3000VA - Power Backup", None),
            ("Storage Array F1", "NetApp AFF A400 - Primary Storage", None),
        ]
        for i, (name, details, secret) in enumerate(items):
            item = InventoryItem(
                owner_id=admin.id, 
                item_name=name, 
                item_details=details,
                secret_notes=secret
            )
            db.session.add(item)
    
    # Add some items for employee
    if InventoryItem.query.filter_by(owner_id=employee.id).count() == 0:
        employee_items = [
            ("Laptop L001", "Dell Latitude 5520 - Assigned to John", None),
            ("Monitor M001", "Dell U2722D - 27 inch 4K", None),
            ("Keyboard K001", "Logitech MX Keys", None),
        ]
        for name, details, secret in employee_items:
            item = InventoryItem(
                owner_id=employee.id,
                item_name=name,
                item_details=details,
                secret_notes=secret
            )
            db.session.add(item)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db() 
    app.run(host='0.0.0.0', port=5003)

