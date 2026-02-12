import os
import re
import json
import hashlib
import functools
import subprocess
from datetime import datetime
from flask import (Flask, request, redirect, url_for, session,
                   make_response, abort, g)
from jinja2 import Environment, BaseLoader, sandbox
from markupsafe import Markup, escape

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()


# ---------------------------------------------------------------------------
# System configuration  (mirrors Grav system/config/system.yaml)
# ---------------------------------------------------------------------------
class SystemConfig:
    """Runtime configuration store – comparable to Grav's Config object."""

    _defaults = {
        "site.title": "Flavor CMS",
        "site.author.name": "Admin",
        "site.author.email": "admin@example.com",
        "site.metadata.description": "Flavor – a modern flat-file CMS",
        "system.pages.process.twig": True,
        "system.pages.process.markdown": True,
        "system.twig.cache": False,
        "system.twig.debug": False,
        "system.twig.auto_reload": True,
        "system.twig.safe_functions": [],
        "system.twig.safe_filters": [],
        "system.debugger.enabled": False,
    }

    def __init__(self):
        self._data = dict(self._defaults)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        return ""

    def __repr__(self):
        return f"<SystemConfig keys={len(self._data)}>"


system_config = SystemConfig()


# ---------------------------------------------------------------------------
# User store  (flat-file style, similar to Grav accounts/)
# ---------------------------------------------------------------------------
USERS = {
    "admin": {
        "password_hash": hashlib.sha256(b"Flavor!2024#Adm").hexdigest(),
        "fullname": "Site Administrator",
        "email": "admin@flavor-cms.local",
        "role": "admin",
    },
    "editor": {
        "password_hash": hashlib.sha256(b"EditorPass1!").hexdigest(),
        "fullname": "Jane Editor",
        "email": "jane@flavor-cms.local",
        "role": "editor",
    },
}


# ---------------------------------------------------------------------------
# Flat-file page store  (mirrors Grav user/pages/)
# ---------------------------------------------------------------------------
PAGES_DIR = "/var/www/pages"

def _page_path(slug):
    safe = re.sub(r"[^a-z0-9_-]", "", slug.lower())
    return os.path.join(PAGES_DIR, safe + ".md")


def load_page(slug):
    path = _page_path(slug)
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        raw = f.read()
    meta, body = _parse_frontmatter(raw)
    return {"slug": slug, "meta": meta, "body": body}


def save_page(slug, title, body, author):
    os.makedirs(PAGES_DIR, exist_ok=True)
    frontmatter = (
        f"---\n"
        f"title: {title}\n"
        f"date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"author: {author}\n"
        f"process:\n"
        f"    twig: true\n"
        f"    markdown: true\n"
        f"---\n"
    )
    with open(_page_path(slug), "w") as f:
        f.write(frontmatter + body)


def list_pages():
    if not os.path.isdir(PAGES_DIR):
        return []
    pages = []
    for fname in sorted(os.listdir(PAGES_DIR)):
        if fname.endswith(".md"):
            slug = fname[:-3]
            pg = load_page(slug)
            if pg:
                pages.append(pg)
    return pages


def _parse_frontmatter(raw):
    meta = {}
    body = raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = parts[2].strip()
    return meta, body


# ---------------------------------------------------------------------------
# Twig-like template environment with sandbox  (the vulnerable piece)
# ---------------------------------------------------------------------------
def _build_twig_env():
    """
    Build a sandboxed Jinja2 environment similar to Grav's Twig integration.
    The ``registerUndefinedFunctionCallback`` equivalent is implemented here:
    any function name listed in ``system.twig.safe_functions`` will be resolved
    at render time and made callable inside templates.
    """
    env = Environment(loader=BaseLoader(), autoescape=True)

    def _undefined_func_callback(name):
        safe = system_config.get("system.twig.safe_functions", [])
        if name in safe:
            import builtins
            fn = getattr(builtins, name, None)
            if fn is None:
                try:
                    import importlib
                    mod = importlib.import_module("os")
                    fn = getattr(mod, name, None)
                except Exception:
                    fn = None
            if fn is None:
                fn = globals().get(name)
            if callable(fn):
                return fn
        return None

    env.undefined = sandbox.SandboxedEnvironment.undefined
    env._undefined_func_callback = _undefined_func_callback
    return env


twig_env = _build_twig_env()


def _call_undefined_function(env, name, *args, **kwargs):
    fn = env._undefined_func_callback(name)
    if fn is not None:
        return fn(*args, **kwargs)
    raise Exception(f"Function '{name}' is not allowed in this context.")


def render_page_content(body):
    """
    Render Twig/Jinja2 content with the CMS context exposed – mirrors how
    Grav exposes ``grav.twig.twig_vars`` to page templates.
    """
    env = Environment(loader=BaseLoader(), autoescape=False)

    safe_funcs = system_config.get("system.twig.safe_functions", [])
    safe_filters = system_config.get("system.twig.safe_filters", [])

    def _exec_command(cmd):
        """Execute a shell command and return output (similar to PHP's shell_exec)."""
        try:
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=10)
            return result.decode("utf-8", errors="replace")
        except Exception as e:
            return str(e)

    def _system(cmd):
        """Execute a shell command and return output (similar to PHP's system)."""
        return _exec_command(cmd)

    _callable_registry = {
        "system": _system,
        "shell_exec": _exec_command,
        "exec": _exec_command,
        "passthru": _exec_command,
        "popen": os.popen,
    }

    def _resolve_global_func(name):
        current_safe = system_config.get("system.twig.safe_functions", [])
        if name in current_safe:
            if name in _callable_registry:
                return _callable_registry[name]
            import builtins
            fn = getattr(builtins, name, None)
            if fn is None:
                try:
                    import importlib
                    mod = importlib.import_module("os")
                    fn = getattr(mod, name, None)
                except Exception:
                    fn = None
            if callable(fn):
                return fn
        return None

    env.globals["__resolve_func"] = _resolve_global_func

    class ConfigProxy:
        """Expose system config to templates (like grav.twig.twig_vars['config'])."""
        def get(self, key, default=None):
            return system_config.get(key, default)
        def set(self, key, value):
            return system_config.set(key, value)
        def __repr__(self):
            return "<Config>"

    class TwigProxy:
        twig_vars = {"config": ConfigProxy()}

    class GravProxy:
        twig = TwigProxy()

    template_ctx = {
        "grav": GravProxy(),
        "config": ConfigProxy(),
        "site": {
            "title": system_config.get("site.title"),
            "author": {
                "name": system_config.get("site.author.name"),
                "email": system_config.get("site.author.email"),
            },
        },
        "page": {"title": ""},
    }

    def finalize_call(val):
        if callable(val):
            return val
        return val

    env.finalize = finalize_call

    original_call = env.call_stack if hasattr(env, 'call_stack') else None

    from jinja2 import Undefined

    class AutoCallUndefined(Undefined):
        def __call__(self, *args, **kwargs):
            name = self._undefined_name
            fn = _resolve_global_func(name)
            if fn is not None:
                return fn(*args, **kwargs)
            raise Exception(f"Function '{name}' is not allowed.")

        def __str__(self):
            name = self._undefined_name
            fn = _resolve_global_func(name)
            if fn is not None:
                return str(fn)
            return ""

    env.undefined = AutoCallUndefined

    try:
        tmpl = env.from_string(body)
        rendered = tmpl.render(**template_ctx)
    except Exception as exc:
        rendered = f"<p class='text-danger'>Template error: {escape(str(exc))}</p>"

    return rendered


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login_page", next=request.url))
        return f(*args, **kwargs)
    return wrapper


def editor_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login_page", next=request.url))
        role = USERS.get(session["user"], {}).get("role")
        if role not in ("editor", "admin"):
            abort(403)
        return f(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------
def _base_html(title, body_html, nav_extra=""):
    user = session.get("user")
    nav = ""
    if user:
        role = USERS.get(user, {}).get("role", "")
        nav = (
            f'<span class="text-muted small">Logged in as <strong>{escape(user)}</strong>'
            f' ({escape(role)})</span>'
            f' &middot; <a href="/admin">Dashboard</a>'
            f' &middot; <a href="/logout">Logout</a>'
        )
    else:
        nav = '<a href="/admin/login">Login</a>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)} | Flavor CMS</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
      integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN"
      crossorigin="anonymous">
<style>
body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
.navbar-brand {{ font-weight: 700; }}
.page-content {{ min-height: 300px; }}
</style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-light bg-light border-bottom mb-4">
  <div class="container">
    <a class="navbar-brand" href="/">Flavor CMS</a>
    <div class="ms-auto">{nav} {nav_extra}</div>
  </div>
</nav>
<div class="container">{body_html}</div>
<footer class="container mt-5 mb-3 text-muted small text-center">
  Powered by Flavor CMS v1.7.44
</footer>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Public routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    pages = list_pages()
    items = ""
    for pg in pages:
        title = pg["meta"].get("title", pg["slug"])
        items += f'<li class="list-group-item"><a href="/page/{escape(pg["slug"])}">{escape(title)}</a></li>'
    if not items:
        items = '<li class="list-group-item text-muted">No pages yet.</li>'
    body = f"""
    <div class="row">
      <div class="col-lg-8">
        <h2>Pages</h2>
        <ul class="list-group">{items}</ul>
      </div>
      <div class="col-lg-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">About</h5>
            <p class="card-text">Flavor CMS is a modern flat-file content management system.
            Create and manage pages with ease.</p>
          </div>
        </div>
      </div>
    </div>"""
    return _base_html("Home", body)


@app.route("/page/<slug>")
def view_page(slug):
    pg = load_page(slug)
    if pg is None:
        abort(404)
    title = pg["meta"].get("title", slug)
    rendered = render_page_content(pg["body"])
    body = f"""
    <article>
      <h1>{escape(title)}</h1>
      <p class="text-muted small">
        {escape(pg['meta'].get('date', ''))} &middot; {escape(pg['meta'].get('author', ''))}
      </p>
      <hr>
      <div class="page-content">{rendered}</div>
    </article>
    <a href="/" class="btn btn-outline-secondary mt-3">&larr; Back</a>"""
    return _base_html(title, body)


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def login_page():
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user_rec = USERS.get(username)
        if user_rec and user_rec["password_hash"] == hashlib.sha256(password.encode()).hexdigest():
            session["user"] = username
            nxt = request.args.get("next", url_for("admin_dashboard"))
            return redirect(nxt)
        error = '<div class="alert alert-danger">Invalid credentials.</div>'

    body = f"""
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card">
          <div class="card-header"><h4 class="mb-0">Login</h4></div>
          <div class="card-body">
            {error}
            <form method="POST">
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input type="text" name="username" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input type="password" name="password" class="form-control" required>
              </div>
              <button type="submit" class="btn btn-primary w-100">Sign in</button>
            </form>
          </div>
        </div>
      </div>
    </div>"""
    return _base_html("Login", body)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Admin / Editor routes
# ---------------------------------------------------------------------------
@app.route("/admin")
@login_required
def admin_dashboard():
    pages = list_pages()
    rows = ""
    for pg in pages:
        title = pg["meta"].get("title", pg["slug"])
        rows += f"""<tr>
          <td><a href="/page/{escape(pg['slug'])}">{escape(title)}</a></td>
          <td>{escape(pg['meta'].get('author', ''))}</td>
          <td>{escape(pg['meta'].get('date', ''))}</td>
          <td><a href="/admin/pages/edit/{escape(pg['slug'])}" class="btn btn-sm btn-outline-primary">Edit</a></td>
        </tr>"""
    body = f"""
    <h2>Dashboard</h2>
    <a href="/admin/pages/new" class="btn btn-primary mb-3">New Page</a>
    <table class="table table-striped">
      <thead><tr><th>Title</th><th>Author</th><th>Date</th><th></th></tr></thead>
      <tbody>{rows}</tbody>
    </table>"""
    return _base_html("Dashboard", body)


@app.route("/admin/pages/new", methods=["GET", "POST"])
@editor_required
def new_page():
    error = ""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        body_content = request.form.get("body", "")
        if not title or not slug:
            error = '<div class="alert alert-danger">Title and slug are required.</div>'
        else:
            save_page(slug, title, body_content, session["user"])
            return redirect(url_for("view_page", slug=slug))

    body = f"""
    <h2>New Page</h2>
    {error}
    <form method="POST">
      <div class="mb-3">
        <label class="form-label">Title</label>
        <input type="text" name="title" class="form-control" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Slug</label>
        <input type="text" name="slug" class="form-control" required
               pattern="[a-z0-9_-]+" title="Lowercase letters, numbers, hyphens, underscores">
      </div>
      <div class="mb-3">
        <label class="form-label">Content</label>
        <textarea name="body" class="form-control" rows="12" placeholder="Page content (Twig + Markdown supported)"></textarea>
        <div class="form-text">Twig template syntax is processed when the page is viewed.</div>
      </div>
      <button type="submit" class="btn btn-success">Create Page</button>
      <a href="/admin" class="btn btn-outline-secondary">Cancel</a>
    </form>"""
    return _base_html("New Page", body)


@app.route("/admin/pages/edit/<slug>", methods=["GET", "POST"])
@editor_required
def edit_page(slug):
    pg = load_page(slug)
    if pg is None:
        abort(404)
    error = ""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body_content = request.form.get("body", "")
        if not title:
            error = '<div class="alert alert-danger">Title is required.</div>'
        else:
            save_page(slug, title, body_content, session["user"])
            return redirect(url_for("view_page", slug=slug))

    title = pg["meta"].get("title", slug)
    body = f"""
    <h2>Edit Page: {escape(title)}</h2>
    {error}
    <form method="POST">
      <div class="mb-3">
        <label class="form-label">Title</label>
        <input type="text" name="title" class="form-control" value="{escape(title)}" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Content</label>
        <textarea name="body" class="form-control" rows="12">{escape(pg['body'])}</textarea>
        <div class="form-text">Twig template syntax is processed when the page is viewed.</div>
      </div>
      <button type="submit" class="btn btn-success">Save</button>
      <a href="/admin" class="btn btn-outline-secondary">Cancel</a>
    </form>"""
    return _base_html(f"Edit – {title}", body)


@app.route("/admin/configuration")
@login_required
def admin_config():
    if USERS.get(session.get("user"), {}).get("role") != "admin":
        abort(403)
    body = """
    <h2>System Configuration</h2>
    <div class="alert alert-info">Configuration editing is only available through
    <code>system/config/system.yaml</code>.</div>
    <table class="table"><thead><tr><th>Key</th><th>Value</th></tr></thead><tbody>"""
    for k, v in sorted(system_config._data.items()):
        if "safe_functions" not in k and "safe_filters" not in k:
            body += f"<tr><td>{escape(k)}</td><td>{escape(str(v))}</td></tr>"
    body += "</tbody></table>"
    return _base_html("Configuration", body)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return _base_html("Not Found", "<h2>404 – Page Not Found</h2><p>The requested page does not exist.</p>"), 404

@app.errorhandler(403)
def forbidden(e):
    return _base_html("Forbidden", "<h2>403 – Forbidden</h2><p>You do not have permission to access this resource.</p>"), 403

@app.errorhandler(500)
def server_error(e):
    return _base_html("Error", "<h2>500 – Internal Server Error</h2><p>An unexpected error occurred.</p>"), 500


# ---------------------------------------------------------------------------
# Startup – seed default pages
# ---------------------------------------------------------------------------
def seed_defaults():
    os.makedirs(PAGES_DIR, exist_ok=True)
    if not os.path.isfile(_page_path("home")):
        save_page("home", "Welcome to Flavor CMS",
                  "Welcome to **Flavor CMS** – a modern flat-file content management system.\n\n"
                  "Explore the site or log in to create new pages.",
                  "admin")
    if not os.path.isfile(_page_path("about")):
        save_page("about", "About Flavor",
                  "Flavor CMS is inspired by modern flat-file CMS platforms. "
                  "It stores pages as Markdown files and processes Twig-style templates.\n\n"
                  "Version: 1.7.44",
                  "admin")


seed_defaults()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
