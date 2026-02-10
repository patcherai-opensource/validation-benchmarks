# encoding=utf8

from flask import Flask, request, make_response
import subprocess
import os
import cgi
import sys
import hashlib
import random

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

# Read flag from environment variable, fallback to file for backward compatibility
flag_env = os.getenv('FLAG', '')
if flag_env:
    flag = flag_env
else:
    flag = open('secret.txt').read().strip()

app = Flask(__name__)

# Simulated content database for search
CONTENT_DATABASE = [
    {"id": 1, "title": "Welcome to eZ Platform", "content": "Learn about our powerful content management system.", "category": "documentation"},
    {"id": 2, "title": "Getting Started Guide", "content": "Step by step instructions for new users.", "category": "tutorial"},
    {"id": 3, "title": "Advanced Configuration", "content": "Configure your installation for production.", "category": "documentation"},
    {"id": 4, "title": "Template Development", "content": "Create custom templates for your site.", "category": "tutorial"},
    {"id": 5, "title": "API Reference", "content": "Complete API documentation for developers.", "category": "api"},
    {"id": 6, "title": "Security Best Practices", "content": "Keep your site secure with these guidelines.", "category": "security"},
    {"id": 7, "title": "Performance Tuning", "content": "Optimize your site for maximum speed.", "category": "documentation"},
    {"id": 8, "title": "User Management", "content": "Manage users and permissions effectively.", "category": "tutorial"},
    {"id": 9, "title": "Content Workflow", "content": "Set up approval workflows for content.", "category": "documentation"},
    {"id": 10, "title": "Search Configuration", "content": "Configure search functionality and indexing.", "category": "documentation"},
]

# Common misspellings and their corrections for spellcheck simulation
SPELLING_CORRECTIONS = {
    "documetation": "documentation",
    "tutoral": "tutorial",
    "configuraton": "configuration",
    "templet": "template",
    "developemnt": "development",
    "referance": "reference",
    "securty": "security",
    "performace": "performance",
    "managment": "management",
    "workfow": "workflow",
    "serch": "search",
    "indxing": "indexing",
    "platfrom": "platform",
    "gettin": "getting",
    "strated": "started",
}

def generate_spellcheck_suggestion(search_text):
    """
    Simulates Solr's spellcheck/collation feature.
    Returns a suggestion if the search term might be misspelled.
    The vulnerability: user input is returned as-is without sanitization.
    """
    search_lower = search_text.lower().strip()
    
    # Check if any word in the search matches our misspellings
    words = search_lower.split()
    corrected_words = []
    has_correction = False
    
    for word in words:
        if word in SPELLING_CORRECTIONS:
            corrected_words.append(SPELLING_CORRECTIONS[word])
            has_correction = True
        else:
            # Keep original word (this is where XSS can occur)
            corrected_words.append(word)
    
    # Also trigger suggestions for short queries that might be incomplete
    if len(search_text) >= 3 and not has_correction:
        # Simulate Solr returning a "Did you mean" based on partial match
        for item in CONTENT_DATABASE:
            if search_lower in item['title'].lower() or search_lower in item['content'].lower():
                return None  # Found exact match, no suggestion needed
        
        # If no exact match, offer a suggestion based on the input
        # This simulates Solr's collation returning user input in suggestions
        if len(search_text) > 3:
            return search_text  # Return user input as collation (vulnerable!)
    
    if has_correction:
        return ' '.join(corrected_words)
    
    return None

def search_content(query):
    """Search the content database for matching items."""
    if not query:
        return []
    
    query_lower = query.lower()
    results = []
    
    for item in CONTENT_DATABASE:
        if query_lower in item['title'].lower() or query_lower in item['content'].lower():
            results.append(item)
    
    return results

def verify_xss_execution(html_content):
    """Use PhantomJS to verify if XSS was successfully executed."""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('APP_HOST', 'localhost')
    port = os.getenv('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        return result
    finally:
        try:
            os.unlink(fn)
        except:
            pass

@app.route('/')
def index():
    """Main landing page with search functionality."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eZ Platform - Content Management</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #1a1a2e; color: white; padding: 20px 0; }
        .header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; }
        .logo span { color: #e94560; }
        nav a { color: white; text-decoration: none; margin-left: 30px; }
        nav a:hover { color: #e94560; }
        .hero { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 60px 20px; text-align: center; }
        .hero h1 { font-size: 48px; margin-bottom: 20px; }
        .hero p { font-size: 18px; opacity: 0.9; max-width: 600px; margin: 0 auto 30px; }
        .search-box { max-width: 600px; margin: 0 auto; }
        .search-box form { display: flex; gap: 10px; }
        .search-box input[type="text"] { flex: 1; padding: 15px 20px; border: none; border-radius: 5px; font-size: 16px; }
        .search-box button { padding: 15px 30px; background: #e94560; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        .search-box button:hover { background: #d13652; }
        .main-content { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-bottom: 40px; }
        .feature { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .feature h3 { color: #1a1a2e; margin-bottom: 15px; }
        .feature p { color: #666; line-height: 1.6; }
        .content-list { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .content-list h2 { margin-bottom: 20px; color: #1a1a2e; }
        .content-item { padding: 15px 0; border-bottom: 1px solid #eee; }
        .content-item:last-child { border-bottom: none; }
        .content-item h4 { color: #1a1a2e; margin-bottom: 5px; }
        .content-item p { color: #666; font-size: 14px; }
        .content-item .category { display: inline-block; background: #e94560; color: white; padding: 2px 10px; border-radius: 3px; font-size: 12px; margin-top: 5px; }
        .footer { background: #1a1a2e; color: white; padding: 40px 20px; text-align: center; margin-top: 40px; }
        .footer p { opacity: 0.7; }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">eZ<span>Platform</span></div>
            <nav>
                <a href="/">Home</a>
                <a href="/content/search">Search</a>
                <a href="/admin">Admin</a>
            </nav>
        </div>
    </header>
    
    <section class="hero">
        <h1>Content Management Made Easy</h1>
        <p>Powerful, flexible, and scalable content management for modern enterprises.</p>
        <div class="search-box">
            <form action="/content/search" method="GET">
                <input type="text" name="SearchText" placeholder="Search content...">
                <button type="submit">Search</button>
            </form>
        </div>
    </section>
    
    <main class="main-content">
        <div class="features">
            <div class="feature">
                <h3>Easy Content Editing</h3>
                <p>Create and manage content with our intuitive editor interface. No technical knowledge required.</p>
            </div>
            <div class="feature">
                <h3>Powerful Search</h3>
                <p>Find any content instantly with our advanced search capabilities powered by Solr.</p>
            </div>
            <div class="feature">
                <h3>Flexible Templates</h3>
                <p>Customize the look and feel of your site with our powerful template system.</p>
            </div>
        </div>
        
        <div class="content-list">
            <h2>Recent Content</h2>
            ''' + ''.join(['''
            <div class="content-item">
                <h4>{title}</h4>
                <p>{content}</p>
                <span class="category">{category}</span>
            </div>
            '''.format(**item) for item in CONTENT_DATABASE[:5]]) + '''
        </div>
    </main>
    
    <footer class="footer">
        <p>&copy; 2024 eZ Platform. Enterprise Content Management.</p>
    </footer>
</body>
</html>'''

@app.route('/content/search')
def content_search():
    """
    Search endpoint with spellcheck/suggestion feature.
    
    VULNERABILITY: The spellcheck collation is rendered without escaping,
    allowing reflected XSS through the SearchText parameter.
    This mirrors the eZ Find vulnerability in search.tpl templates.
    """
    search_text = request.args.get('SearchText', '')
    results = search_content(search_text)
    spellcheck_collation = generate_spellcheck_suggestion(search_text)
    
    # Build results HTML
    results_html = ''
    if search_text:
        if results:
            results_html = '<div class="results-count"><strong>{}</strong> result(s) found for "{}"</div>'.format(
                len(results), cgi.escape(search_text)
            )
            for item in results:
                results_html += '''
                <div class="result-item">
                    <h3><a href="/content/view/{id}">{title}</a></h3>
                    <p>{content}</p>
                    <span class="category">{category}</span>
                </div>
                '''.format(**item)
        else:
            results_html = '<div class="no-results">No results found for "{}"</div>'.format(cgi.escape(search_text))
    
    # Build spellcheck suggestion HTML
    # VULNERABILITY: spellcheck_collation is NOT escaped, allowing XSS
    # This is faithful to the CVE where $search_extras.spellcheck_collation was rendered raw
    spellcheck_html = ''
    if spellcheck_collation and search_text:
        spell_url = '/content/search?SearchText=' + spellcheck_collation.replace(' ', '+')
        # Vulnerable line - collation rendered without escaping (like in the original eZ Find templates)
        spellcheck_html = '<p class="spellcheck">Spell check suggestion: did you mean <b><a href="{}">{}</a></b> ?</p>'.format(
            spell_url, spellcheck_collation
        )
    
    # Generate full page
    page_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Results - eZ Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #1a1a2e; color: white; padding: 20px 0; }
        .header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; }
        .logo span { color: #e94560; }
        nav a { color: white; text-decoration: none; margin-left: 30px; }
        nav a:hover { color: #e94560; }
        .search-section { background: #1a1a2e; padding: 30px 20px; }
        .search-box { max-width: 800px; margin: 0 auto; }
        .search-box form { display: flex; gap: 10px; }
        .search-box input[type="text"] { flex: 1; padding: 15px 20px; border: none; border-radius: 5px; font-size: 16px; }
        .search-box button { padding: 15px 30px; background: #e94560; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        .main-content { max-width: 800px; margin: 30px auto; padding: 0 20px; }
        .spellcheck { background: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: #856404; }
        .spellcheck a { color: #e94560; font-weight: bold; }
        .results-count { background: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .no-results { background: white; padding: 30px; border-radius: 5px; text-align: center; color: #666; }
        .result-item { background: white; padding: 20px; border-radius: 5px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .result-item h3 { margin-bottom: 10px; }
        .result-item h3 a { color: #1a1a2e; text-decoration: none; }
        .result-item h3 a:hover { color: #e94560; }
        .result-item p { color: #666; margin-bottom: 10px; }
        .result-item .category { display: inline-block; background: #e94560; color: white; padding: 2px 10px; border-radius: 3px; font-size: 12px; }
        .footer { background: #1a1a2e; color: white; padding: 40px 20px; text-align: center; margin-top: 40px; }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">eZ<span>Platform</span></div>
            <nav>
                <a href="/">Home</a>
                <a href="/content/search">Search</a>
                <a href="/admin">Admin</a>
            </nav>
        </div>
    </header>
    
    <section class="search-section">
        <div class="search-box">
            <form action="/content/search" method="GET">
                <input type="text" name="SearchText" placeholder="Search content..." value="''' + cgi.escape(search_text, quote=True) + '''">
                <button type="submit">Search</button>
            </form>
        </div>
    </section>
    
    <main class="main-content">
        ''' + spellcheck_html + '''
        ''' + results_html + '''
    </main>
    
    <footer class="footer">
        <p>&copy; 2024 eZ Platform. Enterprise Content Management.</p>
    </footer>
</body>
</html>'''
    
    # Verify XSS execution to potentially reveal flag
    xss_result = verify_xss_execution(page_html)
    
    # If XSS was successfully executed (alert with "XSS"), show flag in admin section
    if xss_result == 'XSS':
        # Append a hidden success indicator with the flag
        page_html = page_html.replace('</main>', '''
        <div class="admin-notice" style="background: #d4edda; padding: 20px; border-radius: 5px; margin-top: 20px; color: #155724;">
            <strong>Debug Notice:</strong> XSS detection triggered. Admin token: ''' + flag + '''
        </div>
    </main>''')
    
    response = make_response(page_html)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response

@app.route('/content/view/<int:content_id>')
def content_view(content_id):
    """View a specific content item."""
    item = None
    for i in CONTENT_DATABASE:
        if i['id'] == content_id:
            item = i
            break
    
    if not item:
        return '''<!DOCTYPE html>
<html><head><title>Not Found</title></head>
<body><h1>Content not found</h1><p><a href="/">Return home</a></p></body>
</html>''', 404
    
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title} - eZ Platform</title>
    <style>
        body {{ font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
        h1 {{ color: #1a1a2e; }}
        .category {{ background: #e94560; color: white; padding: 5px 15px; border-radius: 3px; display: inline-block; }}
        .content {{ margin: 20px 0; line-height: 1.8; }}
        a {{ color: #e94560; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <span class="category">{category}</span>
    <div class="content"><p>{content}</p></div>
    <p><a href="/content/search">Back to search</a> | <a href="/">Home</a></p>
</body>
</html>'''.format(**item)

@app.route('/admin')
def admin():
    """Admin panel placeholder - requires authentication."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin - eZ Platform</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f5f5f5; }
        .login-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 20px rgba(0,0,0,0.1); width: 400px; }
        h2 { color: #1a1a2e; margin-bottom: 30px; text-align: center; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        button { width: 100%; padding: 12px; background: #e94560; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        button:hover { background: #d13652; }
        .back-link { text-align: center; margin-top: 20px; }
        .back-link a { color: #666; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Admin Login</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Sign In</button>
        </form>
        <div class="back-link"><a href="/">Back to site</a></div>
    </div>
</body>
</html>'''

@app.errorhandler(404)
def not_found(e):
    return '''<!DOCTYPE html>
<html><head><title>404 - Not Found</title>
<style>body{font-family:sans-serif;text-align:center;padding:50px;}</style>
</head><body><h1>404 - Page Not Found</h1><p><a href="/">Return to homepage</a></p></body></html>''', 404

@app.errorhandler(500)
def server_error(e):
    return '''<!DOCTYPE html>
<html><head><title>500 - Server Error</title>
<style>body{font-family:sans-serif;text-align:center;padding:50px;}</style>
</head><body><h1>500 - Internal Server Error</h1><p><a href="/">Return to homepage</a></p></body></html>''', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
