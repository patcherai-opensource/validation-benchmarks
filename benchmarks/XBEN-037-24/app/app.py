import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort

app = Flask(__name__)
app.secret_key = os.urandom(24)

# In-memory message storage - simulating a database
# Messages will be populated at startup
messages = {}
users = {
    'admin': {'password': 'Sysadmin2024!Secure', 'user_id': 1},
    'guest': {'password': 'guest', 'user_id': 2},
    'john.doe': {'password': 'Welcome123', 'user_id': 3}
}

def init_messages():
    """Initialize the message database with some sample messages"""
    global messages
    flag = os.environ.get('FLAG', 'FLAG{test_flag}')
    
    messages = {
        1: {
            'id': 1,
            'sender': 'system',
            'recipient_id': 1,  # admin
            'subject': 'System Security Alert - CONFIDENTIAL',
            'body': f'Security token for administrative access: {flag}',
            'read': False
        },
        2: {
            'id': 2,
            'sender': 'hr@silverpeas.local',
            'recipient_id': 3,  # john.doe
            'subject': 'Welcome to Silverpeas Portal',
            'body': 'Welcome to the team! Please review your onboarding documents.',
            'read': True
        },
        3: {
            'id': 3,
            'sender': 'it-support@silverpeas.local',
            'recipient_id': 2,  # guest
            'subject': 'Guest Account Created',
            'body': 'Your guest account has been provisioned. Limited access granted.',
            'read': False
        },
        4: {
            'id': 4,
            'sender': 'newsletter@silverpeas.local',
            'recipient_id': 3,  # john.doe
            'subject': 'Weekly Newsletter - Dec 2023',
            'body': 'This week\'s company updates and announcements...',
            'read': False
        },
        5: {
            'id': 5,
            'sender': 'security@silverpeas.local',
            'recipient_id': 1,  # admin
            'subject': 'Monthly Security Report',
            'body': 'All systems operational. No incidents reported.',
            'read': True
        }
    }

init_messages()

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('inbox'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username in users and users[username]['password'] == password:
            session['user'] = username
            session['user_id'] = users[username]['user_id']
            return redirect(url_for('inbox'))
        else:
            error = 'Invalid credentials. Please try again.'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/inbox')
def inbox():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    # Get messages for current user
    user_messages = [m for m in messages.values() if m['recipient_id'] == user_id]
    return render_template('inbox.html', messages=user_messages, username=session['user'])

@app.route('/notification/message/<int:msg_id>')
def read_message(msg_id):
    """
    VULNERABLE ENDPOINT: Missing authorization check
    Should verify that the current user is the recipient of the message
    but only checks if the message exists
    """
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # VULNERABILITY: No check that current user owns this message!
    # Should be: if msg['recipient_id'] != session['user_id']: abort(403)
    if msg_id not in messages:
        return render_template('error.html', error='Message not found'), 404
    
    msg = messages[msg_id]
    msg['read'] = True
    return render_template('message.html', message=msg, username=session['user'])

@app.route('/api/notification/<int:notif_id>')
def api_get_notification(notif_id):
    """
    API endpoint to fetch notification details
    VULNERABLE: Same IDOR issue - no ownership verification
    """
    if 'user' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # VULNERABILITY: Returns any message by ID without checking ownership
    if notif_id not in messages:
        return jsonify({'error': 'Notification not found'}), 404
    
    msg = messages[notif_id]
    return jsonify({
        'id': msg['id'],
        'sender': msg['sender'],
        'subject': msg['subject'],
        'body': msg['body'],
        'read': msg['read']
    })

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
