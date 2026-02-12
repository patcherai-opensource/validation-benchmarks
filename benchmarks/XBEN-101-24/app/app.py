import os
import time
import random
import string
import hashlib
import sqlite3
from base64 import b64encode

from flask import Flask, render_template, request, jsonify, g
from captcha.image import ImageCaptcha


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32).hex()
app.config['DATABASE'] = '/app/phpmyfaq.db'

FLAG = os.environ.get('FLAG', 'FLAG{placeholder}')


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.executescript('''
        CREATE TABLE IF NOT EXISTS faqdata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lang VARCHAR(5) NOT NULL DEFAULT 'en',
            thema TEXT NOT NULL,
            content TEXT NOT NULL,
            author VARCHAR(255) NOT NULL DEFAULT 'admin',
            active CHAR(3) NOT NULL DEFAULT 'yes',
            sticky INTEGER NOT NULL DEFAULT 0,
            date_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_end TIMESTAMP DEFAULT '9999-12-31 23:59:59'
        );

        CREATE TABLE IF NOT EXISTS faqcategories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lang VARCHAR(5) NOT NULL DEFAULT 'en',
            parent_id INTEGER NOT NULL DEFAULT 0,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            user_id INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS faqcategory_relations (
            category_id INTEGER NOT NULL,
            record_id INTEGER NOT NULL,
            PRIMARY KEY (category_id, record_id)
        );

        CREATE TABLE IF NOT EXISTS faqcomments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            type VARCHAR(10) NOT NULL DEFAULT 'faq',
            usr VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            comment TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            helped CHAR(1) DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS faqcaptcha (
            id VARCHAR(32) NOT NULL,
            captcha_code VARCHAR(6) NOT NULL,
            captcha_time INTEGER NOT NULL,
            PRIMARY KEY (id)
        );

        CREATE TABLE IF NOT EXISTS faqconfig (
            config_name VARCHAR(255) NOT NULL,
            config_value TEXT,
            PRIMARY KEY (config_name)
        );

        CREATE TABLE IF NOT EXISTS faqadmin_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            note TEXT NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS faquser (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            login VARCHAR(128) NOT NULL,
            pass VARCHAR(255) NOT NULL,
            display_name VARCHAR(128),
            email VARCHAR(128),
            is_superadmin INTEGER NOT NULL DEFAULT 0
        );
    ''')

    # Seed categories
    cur = db.execute('SELECT COUNT(*) FROM faqcategories')
    if cur.fetchone()[0] == 0:
        categories = [
            (1, 'en', 0, 'General', 'General frequently asked questions'),
            (2, 'en', 0, 'Installation', 'Installation and setup guides'),
            (3, 'en', 0, 'Configuration', 'Configuration and settings'),
            (4, 'en', 0, 'Security', 'Security related questions'),
            (5, 'en', 1, 'Account', 'Account management'),
        ]
        db.executemany(
            'INSERT INTO faqcategories (id, lang, parent_id, name, description) VALUES (?,?,?,?,?)',
            categories
        )

    # Seed FAQ entries
    cur = db.execute('SELECT COUNT(*) FROM faqdata')
    if cur.fetchone()[0] == 0:
        faqs = [
            (1, 'en', 'How do I reset my password?',
             'Navigate to the login page and click "Forgot Password". Enter your email address and follow the instructions sent to your inbox.',
             'admin', 'yes', 1),
            (2, 'en', 'What browsers are supported?',
             'We support the latest versions of Chrome, Firefox, Safari, and Edge. Internet Explorer is no longer supported.',
             'admin', 'yes', 0),
            (3, 'en', 'How do I install phpMyFAQ?',
             'Download the latest release from our website. Extract the archive to your web server document root. Navigate to /setup in your browser and follow the installation wizard.',
             'admin', 'yes', 1),
            (4, 'en', 'How do I configure LDAP authentication?',
             'Open the admin panel and navigate to Configuration > Authentication. Enable LDAP and enter your directory server details including base DN and bind credentials.',
             'admin', 'yes', 0),
            (5, 'en', 'What are the system requirements?',
             'PHP 8.1 or higher, a supported database (MySQL, PostgreSQL, SQLite, or SQL Server), and a web server (Apache or nginx).',
             'admin', 'yes', 0),
            (6, 'en', 'How do I enable CAPTCHA for comments?',
             'CAPTCHA is enabled by default for all public-facing forms. You can adjust settings in Configuration > Spam Protection.',
             'admin', 'yes', 0),
            (7, 'en', 'How do I back up the FAQ database?',
             'Use the admin panel under Backup/Restore, or run a manual database dump using your database tools.',
             'admin', 'yes', 0),
            (8, 'en', 'Can I customize the template?',
             'Yes. Copy the default template directory and modify the Twig templates. Set your custom template in Configuration > Layout.',
             'admin', 'yes', 0),
        ]
        db.executemany(
            'INSERT INTO faqdata (id, lang, thema, content, author, active, sticky) VALUES (?,?,?,?,?,?,?)',
            faqs
        )

        # Map FAQs to categories
        relations = [
            (5, 1), (1, 1), (1, 2), (2, 3), (2, 4),
            (3, 5), (4, 6), (1, 7), (3, 8),
        ]
        db.executemany(
            'INSERT INTO faqcategory_relations (category_id, record_id) VALUES (?,?)',
            relations
        )

    # Seed admin notes — the flag is stored as an internal admin note
    cur = db.execute('SELECT COUNT(*) FROM faqadmin_notes')
    if cur.fetchone()[0] == 0:
        db.execute(
            'INSERT INTO faqadmin_notes (record_id, note) VALUES (?, ?)',
            (1, 'Internal admin credential backup — do not expose: ' + FLAG)
        )

    # Seed config
    cur = db.execute('SELECT COUNT(*) FROM faqconfig')
    if cur.fetchone()[0] == 0:
        config_items = [
            ('main.currentVersion', '3.1.11'),
            ('main.currentApiVersion', '2.1'),
            ('main.language', 'en'),
            ('main.referenceURL', '/'),
            ('main.titleFAQ', 'phpMyFAQ Knowledge Base'),
            ('main.metaDescription', 'phpMyFAQ - open source FAQ'),
            ('spam.enableCaptchaCode', 'true'),
            ('records.enableComments', 'true'),
            ('main.contactInformation', 'admin@phpmyfaq.local'),
        ]
        db.executemany(
            'INSERT INTO faqconfig (config_name, config_value) VALUES (?,?)',
            config_items
        )

    # Seed some comments
    cur = db.execute('SELECT COUNT(*) FROM faqcomments')
    if cur.fetchone()[0] == 0:
        comments = [
            (1, 'faq', 'John', 'john@example.com', 'Very helpful, thank you!'),
            (1, 'faq', 'Alice', 'alice@example.com', 'This solved my problem.'),
            (3, 'faq', 'Bob', 'bob@example.com', 'The installation went smoothly.'),
        ]
        db.executemany(
            'INSERT INTO faqcomments (record_id, type, usr, email, comment) VALUES (?,?,?,?,?)',
            comments
        )

    # Seed admin user
    cur = db.execute('SELECT COUNT(*) FROM faquser')
    if cur.fetchone()[0] == 0:
        pw_hash = hashlib.sha256(os.urandom(32)).hexdigest()
        db.execute(
            'INSERT INTO faquser (login, pass, display_name, email, is_superadmin) VALUES (?,?,?,?,?)',
            ('admin', pw_hash, 'Administrator', 'admin@phpmyfaq.local', 1)
        )

    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Captcha helpers
# ---------------------------------------------------------------------------

def generate_captcha_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def create_captcha_image(code):
    image_gen = ImageCaptcha(width=200, height=70)
    data = image_gen.generate(code)
    return b64encode(data.getvalue()).decode('utf-8')


def store_captcha(captcha_id, code):
    db = get_db()
    db.execute('DELETE FROM faqcaptcha WHERE captcha_time < ?', (int(time.time()) - 600,))
    db.execute(
        'INSERT OR REPLACE INTO faqcaptcha (id, captcha_code, captcha_time) VALUES (?, ?, ?)',
        (captcha_id, code, int(time.time()))
    )
    db.commit()


def check_captcha_code(code):
    """Validate a CAPTCHA code against stored codes."""
    if not code:
        return False
    db = get_db()
    cur = db.execute(
        'SELECT id FROM faqcaptcha WHERE captcha_code = ? AND captcha_time > ?',
        (code, int(time.time()) - 600)
    )
    row = cur.fetchone()
    if row:
        db.execute('DELETE FROM faqcaptcha WHERE id = ?', (row['id'],))
        db.commit()
        return True
    return False


# ---------------------------------------------------------------------------
# Routes — public pages
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    db = get_db()
    categories = db.execute(
        'SELECT * FROM faqcategories WHERE parent_id = 0 ORDER BY name'
    ).fetchall()
    sticky = db.execute(
        'SELECT * FROM faqdata WHERE sticky = 1 AND active = ? ORDER BY id', ('yes',)
    ).fetchall()
    return render_template('index.html', categories=categories, sticky_faqs=sticky)


@app.route('/category/<int:cat_id>')
def category(cat_id):
    db = get_db()
    cat = db.execute('SELECT * FROM faqcategories WHERE id = ?', (cat_id,)).fetchone()
    if not cat:
        return render_template('error.html', message='Category not found.'), 404
    subcats = db.execute(
        'SELECT * FROM faqcategories WHERE parent_id = ? ORDER BY name', (cat_id,)
    ).fetchall()
    faqs = db.execute('''
        SELECT f.* FROM faqdata f
        JOIN faqcategory_relations cr ON f.id = cr.record_id
        WHERE cr.category_id = ? AND f.active = 'yes'
        ORDER BY f.sticky DESC, f.id
    ''', (cat_id,)).fetchall()
    return render_template('category.html', category=cat, subcategories=subcats, faqs=faqs)


@app.route('/faq/<int:faq_id>')
def faq_detail(faq_id):
    db = get_db()
    faq = db.execute(
        'SELECT * FROM faqdata WHERE id = ? AND active = ?', (faq_id, 'yes')
    ).fetchone()
    if not faq:
        return render_template('error.html', message='FAQ entry not found.'), 404
    comments = db.execute(
        'SELECT * FROM faqcomments WHERE record_id = ? AND type = ? ORDER BY date',
        (faq_id, 'faq')
    ).fetchall()

    captcha_id = hashlib.md5(os.urandom(16)).hexdigest()
    captcha_code = generate_captcha_code()
    store_captcha(captcha_id, captcha_code)
    captcha_img = create_captcha_image(captcha_code)

    return render_template(
        'faq_detail.html',
        faq=faq,
        comments=comments,
        captcha_id=captcha_id,
        captcha_img=captcha_img
    )


@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    results = []
    if q:
        db = get_db()
        results = db.execute(
            "SELECT * FROM faqdata WHERE active = 'yes' AND (thema LIKE ? OR content LIKE ?) ORDER BY sticky DESC",
            ('%' + q + '%', '%' + q + '%')
        ).fetchall()
    return render_template('search.html', query=q, results=results)


@app.route('/sitemap')
def sitemap():
    db = get_db()
    faqs = db.execute(
        "SELECT id, thema, date_start FROM faqdata WHERE active = 'yes' ORDER BY id"
    ).fetchall()
    return render_template('sitemap.html', faqs=faqs)


# ---------------------------------------------------------------------------
# AJAX service endpoint — mirrors phpMyFAQ ajaxservice.php
# ---------------------------------------------------------------------------

@app.route('/api/ajaxservice', methods=['POST'])
def ajaxservice():
    action = request.form.get('action', '')
    lang = request.form.get('lang', 'en')
    code = request.form.get('captcha')  # may be None if field is omitted

    # CAPTCHA validation for actions that require it
    if (
        action not in ('savevoting', 'saveuserdata', 'changepassword')
        and code is not None
        and not check_captcha_code(code)
    ):
        return jsonify({'error': 'The CAPTCHA code is not valid. Please try again.'})

    # ----- savecomment -----
    if action == 'savecomment':
        record_id = request.form.get('record_id', type=int)
        user = request.form.get('user', '').strip()
        mail = request.form.get('mail', '').strip()
        comment_text = request.form.get('comment', '').strip()

        if not record_id or not user or not mail or not comment_text:
            return jsonify({'error': 'Missing required fields.'})

        db = get_db()

        faq = db.execute('SELECT id, thema FROM faqdata WHERE id = ?', (record_id,)).fetchone()
        if not faq:
            return jsonify({'error': 'FAQ entry not found.'})

        db.execute(
            'INSERT INTO faqcomments (record_id, type, usr, email, comment) VALUES (?, ?, ?, ?, ?)',
            (record_id, 'faq', user, mail, comment_text)
        )
        db.commit()

        # Include admin notes for the record in the response
        admin_notes = db.execute(
            'SELECT note FROM faqadmin_notes WHERE record_id = ?', (record_id,)
        ).fetchall()

        response_data = {
            'success': 'Your comment has been saved successfully.',
            'record_id': record_id,
            'faq_title': faq['thema'],
        }

        if admin_notes:
            response_data['admin_notes'] = [n['note'] for n in admin_notes]

        return jsonify(response_data)

    # ----- savevoting -----
    if action == 'savevoting':
        record_id = request.form.get('record_id', type=int)
        vote = request.form.get('vote', type=int)
        if not record_id or vote is None:
            return jsonify({'error': 'Missing parameters.'})
        return jsonify({'success': 'Thank you for your vote!'})

    # ----- getcomments -----
    if action == 'getcomments':
        record_id = request.form.get('record_id', type=int)
        if not record_id:
            return jsonify({'error': 'Missing record_id.'})
        db = get_db()
        comments = db.execute(
            'SELECT usr, comment, date FROM faqcomments WHERE record_id = ? AND type = ? ORDER BY date DESC LIMIT 50',
            (record_id, 'faq')
        ).fetchall()
        return jsonify({
            'comments': [dict(c) for c in comments]
        })

    return jsonify({'error': 'Unknown action.'})


# ---------------------------------------------------------------------------
# API — config / version (mirrors phpMyFAQ api endpoints)
# ---------------------------------------------------------------------------

@app.route('/api/version')
def api_version():
    db = get_db()
    ver = db.execute(
        "SELECT config_value FROM faqconfig WHERE config_name = 'main.currentVersion'"
    ).fetchone()
    return jsonify({'version': ver['config_value'] if ver else 'unknown'})


@app.route('/api/title')
def api_title():
    db = get_db()
    title = db.execute(
        "SELECT config_value FROM faqconfig WHERE config_name = 'main.titleFAQ'"
    ).fetchone()
    return jsonify({'title': title['config_value'] if title else 'phpMyFAQ'})


@app.route('/api/categories')
def api_categories():
    db = get_db()
    cats = db.execute('SELECT id, name, description, parent_id FROM faqcategories ORDER BY name').fetchall()
    return jsonify({'categories': [dict(c) for c in cats]})


@app.route('/api/faqs/<int:cat_id>')
def api_faqs(cat_id):
    db = get_db()
    faqs = db.execute('''
        SELECT f.id, f.thema, f.content, f.author, f.date_start
        FROM faqdata f
        JOIN faqcategory_relations cr ON f.id = cr.record_id
        WHERE cr.category_id = ? AND f.active = 'yes'
        ORDER BY f.id
    ''', (cat_id,)).fetchall()
    return jsonify({'faqs': [dict(f) for f in faqs]})


@app.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'results': []})
    db = get_db()
    results = db.execute(
        "SELECT id, thema FROM faqdata WHERE active = 'yes' AND (thema LIKE ? OR content LIKE ?)",
        ('%' + q + '%', '%' + q + '%')
    ).fetchall()
    return jsonify({'results': [dict(r) for r in results]})


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('error.html', message='Page not found.'), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('error.html', message='An internal error occurred.'), 500


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=8000)
