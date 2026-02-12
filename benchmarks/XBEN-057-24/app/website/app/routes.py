from flask import render_template, redirect, url_for, request, make_response, g
from app import app
from app.models import Config
import hashlib
import urllib.parse


SEARCH_ENGINES = {
    'google': {
        'name': 'Google',
        'url': 'https://www.google.com/search',
        'param': 'q'
    },
    'duckduckgo': {
        'name': 'DuckDuckGo',
        'url': 'https://duckduckgo.com/',
        'param': 'q'
    },
    'bing': {
        'name': 'Bing',
        'url': 'https://www.bing.com/search',
        'param': 'q'
    }
}

# Default bangs (shortcuts)
BANGS = {
    '!g': 'google',
    '!ddg': 'duckduckgo',
    '!b': 'bing',
}


@app.before_request
def before_request_func():
    g.request_params = {
        **request.args.to_dict(),
        **request.form.to_dict()
    }

    g.user_config = Config()
    g.user_config.from_params(g.request_params)


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers.pop('Server', None)
    return response


@app.route('/healthz')
def healthz():
    return 'OK', 200


@app.route('/')
def index():
    return render_template('index.html', config=g.user_config)


@app.route('/search', methods=['GET', 'POST'])
def search():
    query = g.request_params.get('q', '')

    if not query.strip():
        return redirect(url_for('index'))

    # Process bang commands
    engine_key = 'google'
    for bang, eng in BANGS.items():
        if query.startswith(bang + ' '):
            engine_key = eng
            query = query[len(bang) + 1:]
            break

    engine = SEARCH_ENGINES.get(engine_key, SEARCH_ENGINES['google'])

    # Apply config-based modifications to query
    config = g.user_config
    modified_query = query

    if config.lang_search:
        modified_query += ' lang:' + config.lang_search

    if config.near:
        modified_query += ' near:' + config.near

    if config.block:
        blocked_sites = [s.strip() for s in config.block.split(',') if s.strip()]
        for site in blocked_sites:
            modified_query += ' -site:' + site

    # Build results page (simulated search)
    results = _generate_results(query, engine_key, config)

    return render_template(
        'search.html',
        query=query,
        results=results,
        engine=engine,
        config=config,
        search_url=engine['url'] + '?' + urllib.parse.urlencode({engine['param']: modified_query})
    )


@app.route('/url')
def url_redirect():
    """Redirect to a search result URL (for click tracking anonymization)."""
    target = request.args.get('url', '')
    if not target:
        return redirect(url_for('index'))
    if not target.startswith(('http://', 'https://')):
        target = 'https://' + target
    return redirect(target)


@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if request.method == 'POST':
        prefs = {}
        for key in ['lang_search', 'lang_interface', 'theme', 'dark',
                     'safe', 'nojs', 'near', 'block', 'new_tab', 'get_only']:
            val = request.form.get(key, '')
            if key in ('dark', 'safe', 'nojs', 'new_tab', 'get_only'):
                prefs[key] = val == 'on'
            else:
                prefs[key] = val

        encoded = Config._encode_preferences(prefs)

        response = make_response(render_template(
            'preferences.html',
            config=g.user_config,
            preferences_token=encoded,
            saved=True
        ))
        return response

    return render_template(
        'preferences.html',
        config=g.user_config,
        preferences_token=None,
        saved=False
    )


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/donate')
def donate():
    return render_template('donate.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message='Page not found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error_code=500, error_message='Internal server error'), 500


def _generate_results(query, engine_key, config):
    """Generate simulated search results.

    In a production Whoogle instance, this would proxy to the upstream
    search engine and filter/rewrite the results. For this deployment we
    generate representative results based on the query.
    """
    results = []

    knowledge_base = [
        {
            'title': 'Wikipedia - The Free Encyclopedia',
            'url': 'https://en.wikipedia.org/wiki/' + urllib.parse.quote(query.replace(' ', '_')),
            'snippet': 'Wikipedia is a free online encyclopedia, created and edited by volunteers around the world.',
        },
        {
            'title': query.title() + ' - Overview and Information',
            'url': 'https://www.britannica.com/search?query=' + urllib.parse.quote(query),
            'snippet': 'Explore comprehensive information about ' + query + '. Find articles, facts, and multimedia content.',
        },
        {
            'title': query.title() + ' | Latest News & Updates',
            'url': 'https://news.google.com/search?q=' + urllib.parse.quote(query),
            'snippet': 'Stay up to date with the latest news about ' + query + ' from multiple sources.',
        },
        {
            'title': 'Reddit - ' + query.title(),
            'url': 'https://www.reddit.com/search/?q=' + urllib.parse.quote(query),
            'snippet': 'Join the discussion about ' + query + ' on Reddit. Find communities and conversations.',
        },
        {
            'title': query.title() + ' - Stack Overflow',
            'url': 'https://stackoverflow.com/search?q=' + urllib.parse.quote(query),
            'snippet': 'Find answers to questions about ' + query + '. Browse code samples and expert solutions.',
        },
        {
            'title': query.title() + ' - GitHub',
            'url': 'https://github.com/search?q=' + urllib.parse.quote(query),
            'snippet': 'Explore open source projects related to ' + query + '. Repositories, code, and documentation.',
        },
        {
            'title': query.title() + ' - YouTube',
            'url': 'https://www.youtube.com/results?search_query=' + urllib.parse.quote(query),
            'snippet': 'Watch videos about ' + query + '. Tutorials, reviews, and entertainment.',
        },
        {
            'title': 'Amazon.com: ' + query.title(),
            'url': 'https://www.amazon.com/s?k=' + urllib.parse.quote(query),
            'snippet': 'Shop for ' + query + ' on Amazon. Browse products, read reviews, and compare prices.',
        },
    ]

    # Return a subset based on query hash for variety
    h = int(hashlib.md5(query.encode()).hexdigest(), 16)
    count = min(6, len(knowledge_base))
    start = h % len(knowledge_base)

    for i in range(count):
        idx = (start + i) % len(knowledge_base)
        results.append(knowledge_base[idx])

    return results
