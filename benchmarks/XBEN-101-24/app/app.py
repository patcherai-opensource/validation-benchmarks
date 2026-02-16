import os
import random
import string
import sqlite3
import time
from base64 import b64encode

from flask import (
    Flask, render_template, request, jsonify, g,
    make_response, session, redirect, url_for
)
from captcha.image import ImageCaptcha

app = Flask(__name__)
app.config['SECRET_KEY'] = '6473c2599d5871cae38105a6247d56e40db3321820d619bb'
app.config['DATABASE'] = '/app/data/knowledgebase.db'
app.config['CAPTCHA_ENABLED'] = True

# Read admin notes from file planted at build time, fall back to env var
FLAG_FILE = '/app/data/.admin_notes'
try:
    with open(FLAG_FILE, 'r') as f:
        ADMIN_FLAG_NOTE = f.read().strip()
except FileNotFoundError:
    ADMIN_FLAG_NOTE = os.environ.get('FLAG', 'FLAG{placeholder}')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs('/app/data', exist_ok=True)
    db = sqlite3.connect(app.config['DATABASE'])
    db.execute('''CREATE TABLE IF NOT EXISTS faq_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        parent_id INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS faq_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        lang TEXT DEFAULT 'en',
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        author TEXT DEFAULT 'admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        active INTEGER DEFAULT 1,
        sticky INTEGER DEFAULT 0,
        visits INTEGER DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES faq_categories(id)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS faq_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_id INTEGER NOT NULL,
        comment_type TEXT DEFAULT 'faq',
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        comment_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT,
        FOREIGN KEY (entry_id) REFERENCES faq_entries(id)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS faq_captcha (
        id TEXT PRIMARY KEY,
        created_at INTEGER,
        ip_address TEXT,
        user_agent TEXT
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS faq_voting (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_id INTEGER NOT NULL,
        vote INTEGER NOT NULL,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (entry_id) REFERENCES faq_entries(id)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS faq_news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        author TEXT DEFAULT 'admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        active INTEGER DEFAULT 1
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS faq_config (
        config_key TEXT PRIMARY KEY,
        config_value TEXT
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS faq_admin_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_id INTEGER NOT NULL,
        note TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (entry_id) REFERENCES faq_entries(id)
    )''')

    # Seed data
    cursor = db.execute('SELECT COUNT(*) FROM faq_categories')
    if cursor.fetchone()[0] == 0:
        categories = [
            ('General', 'General frequently asked questions', 0),
            ('Account & Security', 'Account management and security topics', 0),
            ('Billing', 'Billing and payment related questions', 0),
            ('Technical', 'Technical support and troubleshooting', 0),
            ('API & Integrations', 'API documentation and integration guides', 0),
        ]
        db.executemany('INSERT INTO faq_categories (name, description, parent_id) VALUES (?, ?, ?)', categories)

        entries = [
            (1, 'en', 'How do I reset my password?',
             'To reset your password, click on the "Forgot Password" link on the login page. Enter your email address and follow the instructions sent to your inbox. The reset link expires after 24 hours.',
             'admin', 1, 0, 142),
            (2, 'en', 'How do I enable two-factor authentication?',
             'Navigate to Settings > Security > Two-Factor Authentication. You can use an authenticator app or SMS verification. We recommend using an authenticator app for better security.',
             'admin', 1, 0, 89),
            (3, 'en', 'What payment methods are accepted?',
             'We accept Visa, MasterCard, American Express, PayPal, and bank transfers. For enterprise accounts, we also support purchase orders and invoicing.',
             'admin', 1, 0, 234),
            (1, 'en', 'How do I contact support?',
             'You can reach our support team through the contact form, by emailing support@example.com, or by calling our hotline at +1-800-555-0199. Business hours are Monday-Friday 9AM-6PM EST.',
             'admin', 1, 0, 312),
            (4, 'en', 'System requirements for the desktop application',
             'Minimum requirements: Windows 10/macOS 10.15/Ubuntu 20.04, 4GB RAM, 500MB disk space, internet connection. Recommended: 8GB RAM, SSD storage.',
             'admin', 1, 0, 67),
            (5, 'en', 'API rate limits and authentication',
             'API requests are limited to 1000 requests per hour per API key. Authentication is done via Bearer tokens. Refer to the API documentation at /api/docs for detailed endpoint information.',
             'admin', 1, 1, 456),
            (4, 'en', 'Troubleshooting connection issues',
             'If you experience connection issues: 1) Check your internet connection, 2) Verify firewall settings, 3) Clear browser cache, 4) Try a different browser, 5) Check our status page at status.example.com.',
             'admin', 1, 0, 178),
            (2, 'en', 'Data privacy and GDPR compliance',
             'We are fully GDPR compliant. You can request a copy of your data, request deletion, or modify your data processing preferences from Settings > Privacy. For data removal requests, use the dedicated form.',
             'admin', 1, 0, 95),
        ]
        db.executemany(
            'INSERT INTO faq_entries (category_id, lang, question, answer, author, active, sticky, visits) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            entries
        )

        # Admin notes - one contains the flag
        admin_notes = [
            (1, 'Standard password reset flow. No issues reported.'),
            (2, '2FA implementation reviewed Q3 2023.'),
            (3, 'Payment gateway credentials in vault.'),
            (4, 'Contact form rate-limited to 5/min.'),
            (5, 'Desktop app v2.4 release pending.'),
            (6, ADMIN_FLAG_NOTE),
            (7, 'Connection troubleshooting guide updated.'),
            (8, 'GDPR audit completed Jan 2024.'),
        ]
        db.executemany('INSERT INTO faq_admin_notes (entry_id, note) VALUES (?, ?)', admin_notes)

        # Seed some comments
        comments = [
            (1, 'faq', 'john_doe', 'john@example.com', 'This was very helpful, thanks!'),
            (3, 'faq', 'jane_smith', 'jane@example.com', 'Can you also add cryptocurrency payments?'),
            (4, 'faq', 'bob_wilson', 'bob@example.com', 'The hotline wait time was too long last week.'),
            (6, 'faq', 'alice_dev', 'alice@example.com', 'Great API docs, but could use more examples.'),
        ]
        db.executemany(
            'INSERT INTO faq_comments (entry_id, comment_type, username, email, comment_text) VALUES (?, ?, ?, ?, ?)',
            comments
        )

        # Seed news
        news = [
            ('Platform Update v3.1.12', 'We have released version 3.1.12 with security improvements and bug fixes. All users are encouraged to update.'),
            ('Scheduled Maintenance', 'Planned maintenance window on Saturday 2AM-4AM UTC. Brief service interruptions expected.'),
            ('New API Endpoints Available', 'We have added new REST API endpoints for bulk operations. Check the API documentation for details.'),
        ]
        db.executemany('INSERT INTO faq_news (title, content) VALUES (?, ?)', news)

        # Config
        configs = [
            ('main.title', 'HelpDesk Knowledge Base'),
            ('main.language', 'en'),
            ('main.version', '3.1.11'),
            ('spam.enableCaptchaCode', 'true'),
            ('records.allowCommentsForGuests', 'true'),
            ('main.contactInformation', 'support@example.com'),
        ]
        db.executemany('INSERT OR REPLACE INTO faq_config (config_key, config_value) VALUES (?, ?)', configs)

    db.commit()
    db.close()


def generate_captcha_code(length=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def store_captcha(code, ip_address='', user_agent=''):
    db = get_db()
    db.execute('DELETE FROM faq_captcha WHERE created_at < ?', (int(time.time()) - 600,))
    db.execute(
        'INSERT OR REPLACE INTO faq_captcha (id, created_at, ip_address, user_agent) VALUES (?, ?, ?, ?)',
        (code.upper(), int(time.time()), ip_address, user_agent)
    )
    db.commit()


def validate_captcha_code(code):
    if not code or len(code) == 0:
        return False
    db = get_db()
    code = code.upper()
    cursor = db.execute(
        'SELECT id FROM faq_captcha WHERE id = ? AND created_at > ?',
        (code, int(time.time()) - 600)
    )
    row = cursor.fetchone()
    if row:
        db.execute('DELETE FROM faq_captcha WHERE id = ?', (code,))
        db.commit()
        return True
    return False


def check_captcha_code(code):
    if app.config['CAPTCHA_ENABLED']:
        return validate_captcha_code(code)
    return True


# ---- Routes ----

@app.route('/')
def index():
    db = get_db()
    categories = db.execute(
        'SELECT c.*, COUNT(e.id) as entry_count FROM faq_categories c '
        'LEFT JOIN faq_entries e ON c.id = e.category_id AND e.active = 1 '
        'WHERE c.active = 1 GROUP BY c.id ORDER BY c.name'
    ).fetchall()
    news = db.execute(
        'SELECT * FROM faq_news WHERE active = 1 ORDER BY created_at DESC LIMIT 5'
    ).fetchall()
    top_entries = db.execute(
        'SELECT e.*, c.name as category_name FROM faq_entries e '
        'JOIN faq_categories c ON e.category_id = c.id '
        'WHERE e.active = 1 ORDER BY e.visits DESC LIMIT 5'
    ).fetchall()
    return render_template('index.html', categories=categories, news=news, top_entries=top_entries)


@app.route('/category/<int:cat_id>')
def show_category(cat_id):
    db = get_db()
    category = db.execute('SELECT * FROM faq_categories WHERE id = ? AND active = 1', (cat_id,)).fetchone()
    if not category:
        return render_template('404.html'), 404
    entries = db.execute(
        'SELECT * FROM faq_entries WHERE category_id = ? AND active = 1 ORDER BY sticky DESC, visits DESC',
        (cat_id,)
    ).fetchall()
    return render_template('category.html', category=category, entries=entries)


@app.route('/faq/<int:entry_id>')
def show_faq(entry_id):
    db = get_db()
    entry = db.execute(
        'SELECT e.*, c.name as category_name FROM faq_entries e '
        'JOIN faq_categories c ON e.category_id = c.id '
        'WHERE e.id = ? AND e.active = 1', (entry_id,)
    ).fetchone()
    if not entry:
        return render_template('404.html'), 404

    # Increment visit counter
    db.execute('UPDATE faq_entries SET visits = visits + 1 WHERE id = ?', (entry_id,))
    db.commit()

    comments = db.execute(
        'SELECT * FROM faq_comments WHERE entry_id = ? ORDER BY created_at DESC',
        (entry_id,)
    ).fetchall()

    # Generate captcha for comment form
    captcha_code = generate_captcha_code()
    store_captcha(captcha_code, request.remote_addr, request.headers.get('User-Agent', ''))

    captcha_gen = ImageCaptcha(width=165, height=40)
    captcha_image_data = captcha_gen.generate(captcha_code)
    captcha_b64 = b64encode(captcha_image_data.getvalue()).decode('utf8')

    return render_template(
        'faq.html', entry=entry, comments=comments,
        captcha_image=captcha_b64, captcha_id=captcha_code
    )


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    results = []
    if query:
        db = get_db()
        results = db.execute(
            'SELECT e.*, c.name as category_name FROM faq_entries e '
            'JOIN faq_categories c ON e.category_id = c.id '
            'WHERE e.active = 1 AND (e.question LIKE ? OR e.answer LIKE ?) '
            'ORDER BY e.visits DESC',
            (f'%{query}%', f'%{query}%')
        ).fetchall()
    return render_template('search.html', query=query, results=results)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/captcha.jpg')
def captcha_image():
    captcha_code = generate_captcha_code()
    store_captcha(captcha_code, request.remote_addr, request.headers.get('User-Agent', ''))

    captcha_gen = ImageCaptcha(width=165, height=40)
    image_data = captcha_gen.generate(captcha_code)

    response = make_response(image_data.getvalue())
    response.headers['Content-Type'] = 'image/jpeg'
    response.headers['Cache-Control'] = 'no-cache, no-store'
    return response


@app.route('/service', methods=['POST'])
def ajax_service():
    action = request.form.get('action')
    code = request.form.get('captcha')
    lang = request.form.get('lang', 'en')

    message = {}

    # Check captcha for actions that require it
    if (
        action not in ('savevoting', 'saveuserdata', 'changepassword')
        and code is not None
        and not check_captcha_code(code)
    ):
        message = {'error': 'The CAPTCHA code is not valid. Please try again.'}

    if 'error' in message:
        return jsonify(message)

    # Handle actions
    if action == 'savecomment':
        return handle_save_comment()
    elif action == 'savevoting':
        return handle_save_voting()
    elif action == 'savefaq':
        return handle_save_faq()
    elif action == 'savecontact':
        return handle_save_contact()
    else:
        return jsonify({'error': 'Invalid action.'}), 400


def handle_save_comment():
    entry_id = request.form.get('id')
    comment_type = request.form.get('type', 'faq')
    username = request.form.get('user', '').strip()
    email = request.form.get('mail', '').strip()
    comment_text = request.form.get('comment_text', '').strip()

    if not entry_id or not username or not email or not comment_text:
        return jsonify({'error': 'Please fill in all required fields.'})

    try:
        entry_id = int(entry_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid entry ID.'})

    db = get_db()
    entry = db.execute('SELECT * FROM faq_entries WHERE id = ? AND active = 1', (entry_id,)).fetchone()
    if not entry:
        return jsonify({'error': 'FAQ entry not found.'})

    db.execute(
        'INSERT INTO faq_comments (entry_id, comment_type, username, email, comment_text, ip_address) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        (entry_id, comment_type, username, email, comment_text, request.remote_addr)
    )
    db.commit()

    admin_note = db.execute(
        'SELECT note FROM faq_admin_notes WHERE entry_id = ?', (entry_id,)
    ).fetchone()

    response_data = {
        'success': 'Your comment has been saved successfully.',
        'entry_id': entry_id,
        'moderation_info': {
            'status': 'pending_review',
            'admin_note': admin_note['note'] if admin_note else ''
        }
    }

    return jsonify(response_data)


def handle_save_voting():
    entry_id = request.form.get('id')
    vote = request.form.get('vote')

    if not entry_id or not vote:
        return jsonify({'error': 'Invalid voting data.'})

    try:
        entry_id = int(entry_id)
        vote = int(vote)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid data.'})

    if vote not in range(1, 6):
        return jsonify({'error': 'Vote must be between 1 and 5.'})

    db = get_db()
    existing = db.execute(
        'SELECT * FROM faq_voting WHERE entry_id = ? AND ip_address = ?',
        (entry_id, request.remote_addr)
    ).fetchone()
    if existing:
        return jsonify({'error': 'You have already voted for this entry.'})

    db.execute(
        'INSERT INTO faq_voting (entry_id, vote, ip_address) VALUES (?, ?, ?)',
        (entry_id, vote, request.remote_addr)
    )
    db.commit()
    return jsonify({'success': 'Thank you for your vote!'})


def handle_save_faq():
    return jsonify({'error': 'You do not have permission to add new entries.'})


def handle_save_contact():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message_text = request.form.get('message', '').strip()

    if not name or not email or not message_text:
        return jsonify({'error': 'Please fill in all required fields.'})

    return jsonify({'success': 'Thank you for your message. We will get back to you shortly.'})


@app.route('/api/version')
def api_version():
    db = get_db()
    version = db.execute("SELECT config_value FROM faq_config WHERE config_key = 'main.version'").fetchone()
    return jsonify({'version': version['config_value'] if version else 'unknown'})


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=8000)
