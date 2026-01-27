from flask import Flask, request, redirect, render_template_string, make_response
import re
import os

app = Flask(__name__)

FLAG = os.environ.get('FLAG', '@FLAG@')

# Supported locales
SUPPORTED_LOCALES = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko']

# HTML templates
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="{{ locale }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GlobalTranslate - International Content Platform</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .locale-select {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin-bottom: 30px;
        }
        .locale-btn {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            transition: background 0.3s;
        }
        .locale-btn:hover {
            background: #5a6fd6;
        }
        .locale-btn.active {
            background: #4c5dc4;
        }
        .content {
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .message {
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        form {
            margin-top: 20px;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button[type="submit"] {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button[type="submit"]:hover {
            background: #5a6fd6;
        }
        .flag-display {
            background: #28a745;
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-family: monospace;
            font-size: 14px;
            word-break: break-all;
        }
        .info {
            font-size: 12px;
            color: #888;
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 GlobalTranslate</h1>
        <p class="subtitle">International Content Management Platform</p>
        {{ content | safe }}
    </div>
</body>
</html>
'''

MESSAGES = {
    'en': {'welcome': 'Welcome to GlobalTranslate', 'select_lang': 'Select your language'},
    'es': {'welcome': 'Bienvenido a GlobalTranslate', 'select_lang': 'Seleccione su idioma'},
    'fr': {'welcome': 'Bienvenue sur GlobalTranslate', 'select_lang': 'Sélectionnez votre langue'},
    'de': {'welcome': 'Willkommen bei GlobalTranslate', 'select_lang': 'Wählen Sie Ihre Sprache'},
    'it': {'welcome': 'Benvenuto su GlobalTranslate', 'select_lang': 'Seleziona la tua lingua'},
    'pt': {'welcome': 'Bem-vindo ao GlobalTranslate', 'select_lang': 'Selecione seu idioma'},
    'ru': {'welcome': 'Добро пожаловать в GlobalTranslate', 'select_lang': 'Выберите язык'},
    'zh': {'welcome': '欢迎使用 GlobalTranslate', 'select_lang': '选择您的语言'},
    'ja': {'welcome': 'GlobalTranslateへようこそ', 'select_lang': '言語を選択してください'},
    'ko': {'welcome': 'GlobalTranslate에 오신 것을 환영합니다', 'select_lang': '언어를 선택하세요'},
}

def get_locale_pattern(locale_prefix):
    """
    Build a regex pattern for URL matching based on the locale prefix.
    This mimics Django's LocalePrefixPattern.regex property.
    VULNERABLE: locale_prefix is passed directly to re.compile without escaping
    """
    # This is the vulnerable code - similar to Django's CVE-2022-41323
    # The locale is not escaped before being compiled as regex
    pattern = re.compile(locale_prefix)
    return pattern

def validate_locale_pattern(locale):
    """
    Validate that the locale matches the expected pattern.
    Uses regex compilation to check locale validity.
    """
    try:
        # Attempt to compile the locale as a regex pattern
        # This mimics Django's behavior before the fix
        pattern = get_locale_pattern(locale)
        
        # Check if locale matches supported patterns
        for supported in SUPPORTED_LOCALES:
            if pattern.match(supported):
                return True, supported
        return False, None
    except re.error as e:
        # Regex compilation error - this is where the vulnerability manifests
        # In the original CVE, this caused DoS. Here, we make it reveal the flag
        # to create a CTF-appropriate exploit scenario
        return 'error', str(e)

@app.route('/')
def index():
    """Main landing page"""
    locale_buttons = ''.join([
        f'<a href="/{loc}/" class="locale-btn">{loc.upper()}</a>'
        for loc in SUPPORTED_LOCALES
    ])
    
    content = f'''
        <div class="locale-select">
            {locale_buttons}
        </div>
        <div class="content">
            <h3>Welcome to GlobalTranslate</h3>
            <p>Select a language above to view localized content, or use the custom locale feature below.</p>
            
            <form action="/set-locale" method="POST">
                <label>Custom Locale Code:</label>
                <input type="text" name="locale" placeholder="Enter locale code (e.g., en, es, fr)">
                <button type="submit">Set Locale</button>
            </form>
        </div>
        <p class="info">Powered by i18n URL patterns • Version 3.2.15</p>
    '''
    
    return render_template_string(BASE_TEMPLATE, locale='en', content=content)

@app.route('/set-locale', methods=['POST'])
def set_locale():
    """Handle custom locale setting - VULNERABLE ENDPOINT"""
    locale = request.form.get('locale', 'en')
    
    # Validate the locale using regex compilation
    result, detail = validate_locale_pattern(locale)
    
    if result == 'error':
        # Regex error occurred - this triggers the vulnerability path
        # In a real scenario, this would be DoS. For CTF, we reveal the flag
        # This simulates a scenario where the regex error bypasses validation
        # and exposes sensitive data
        content = f'''
            <div class="message error">
                <strong>Locale Pattern Error:</strong> {detail}
            </div>
            <div class="content">
                <p>An unexpected error occurred while processing your locale request.</p>
                <p>The system encountered a regex compilation issue with the provided input.</p>
            </div>
            <div class="flag-display">
                <strong>Debug Mode Active - Configuration Dump:</strong><br>
                SECRET_KEY: {FLAG}
            </div>
            <p class="info">Error logged for review. Contact admin@globaltranslate.local</p>
        '''
    elif result is True:
        # Valid locale found
        return redirect(f'/{detail}/')
    else:
        # Invalid locale but no error
        content = f'''
            <div class="message error">
                <strong>Invalid Locale:</strong> '{locale}' is not a supported locale code.
            </div>
            <div class="content">
                <p>Please select from our supported locales: {', '.join(SUPPORTED_LOCALES)}</p>
                <a href="/" class="locale-btn">Back to Home</a>
            </div>
        '''
    
    return render_template_string(BASE_TEMPLATE, locale='en', content=content)

@app.route('/<locale>/')
def localized_page(locale):
    """Display localized content"""
    # Validate locale via URL parameter as well
    result, detail = validate_locale_pattern(locale)
    
    if result == 'error':
        # Same vulnerability through URL parameter
        content = f'''
            <div class="message error">
                <strong>URL Pattern Error:</strong> {detail}
            </div>
            <div class="content">
                <p>Failed to process internationalized URL pattern.</p>
            </div>
            <div class="flag-display">
                <strong>Debug Mode Active - Configuration Dump:</strong><br>
                SECRET_KEY: {FLAG}
            </div>
        '''
        return render_template_string(BASE_TEMPLATE, locale='en', content=content)
    
    if locale in MESSAGES:
        messages = MESSAGES[locale]
        locale_buttons = ''.join([
            f'<a href="/{loc}/" class="locale-btn {"active" if loc == locale else ""}">{loc.upper()}</a>'
            for loc in SUPPORTED_LOCALES
        ])
        
        content = f'''
            <div class="locale-select">
                {locale_buttons}
            </div>
            <div class="content">
                <h3>{messages["welcome"]}</h3>
                <p>{messages["select_lang"]}</p>
            </div>
            <p class="info">Currently viewing: {locale.upper()} • i18n URL patterns enabled</p>
        '''
        return render_template_string(BASE_TEMPLATE, locale=locale, content=content)
    else:
        content = f'''
            <div class="message error">
                <strong>Locale Not Found:</strong> '{locale}' is not available.
            </div>
            <div class="content">
                <p>Available locales: {', '.join(SUPPORTED_LOCALES)}</p>
                <a href="/" class="locale-btn">Back to Home</a>
            </div>
        '''
        return render_template_string(BASE_TEMPLATE, locale='en', content=content)

@app.route('/health')
def health():
    """Health check endpoint"""
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
