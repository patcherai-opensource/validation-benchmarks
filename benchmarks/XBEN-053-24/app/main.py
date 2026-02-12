import os
import re
import hashlib
import secrets
import sqlite3
from datetime import datetime

from fastapi import FastAPI, Request, Form, HTTPException, Cookie, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from jinja2 import Environment, BaseLoader, TemplateSyntaxError, UndefinedError


# ---------------------------------------------------------------------------
# Application configuration (mirrors Grav system/config/system.yaml)
# ---------------------------------------------------------------------------
class SystemConfig:
    """Runtime configuration store — similar to Grav's Config object."""

    def __init__(self):
        self._data = {
            "system": {
                "twig": {
                    "cache": True,
                    "debug": False,
                    "auto_reload": True,
                    "autoescape": False,
                    "safe_functions": ["date", "url", "dump"],
                    "safe_filters": ["capitalize", "lower", "upper", "trim", "nl2br"],
                },
                "pages": {
                    "theme": "flavor",
                    "markdown": {"extra": True},
                    "process": {"twig": True, "markdown": True},
                },
                "site": {
                    "title": "Flavor CMS",
                    "description": "A Modern Flat-File CMS",
                    "author": {"name": "Admin", "email": "admin@flavor-cms.local"},
                },
            }
        }

    def get(self, dotpath, default=None):
        parts = dotpath.split(".")
        node = self._data
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return default
        return node

    def set(self, dotpath, value):
        parts = dotpath.split(".")
        node = self._data
        for p in parts[:-1]:
            if p not in node:
                node[p] = {}
            node = node[p]
        node[parts[-1]] = value


config = SystemConfig()

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
DB_PATH = "/app/data/flavor.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs("/app/data", exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT NOT NULL DEFAULT 'editor',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER,
            published INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Seed default users
    def _hash(pw):
        return hashlib.sha256(pw.encode()).hexdigest()

    try:
        c.execute(
            "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
            ("admin", _hash("Fl@vorAdm1n!2024"), "admin@flavor-cms.local", "admin"),
        )
    except sqlite3.IntegrityError:
        pass
    try:
        c.execute(
            "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
            ("editor", _hash("editor"), "editor@flavor-cms.local", "editor"),
        )
    except sqlite3.IntegrityError:
        pass

    # Seed some pages
    default_pages = [
        (
            "home",
            "Home",
            "# Welcome to Flavor CMS\n\nA modern, fast, flat-file content management system.\n\nFlavor CMS is designed for speed and simplicity.",
            1,
        ),
        (
            "about",
            "About",
            "# About Flavor CMS\n\nFlavor CMS v1.7.44 is a modern flat-file CMS.\n\nBuilt with flexibility and performance in mind.",
            1,
        ),
        (
            "features",
            "Features",
            "# Features\n\n- Markdown support\n- Twig templating\n- Flat-file architecture\n- Plugin ecosystem\n- Multi-language support",
            1,
        ),
    ]
    for slug, title, content, author_id in default_pages:
        try:
            c.execute(
                "INSERT INTO pages (slug, title, content, author_id) VALUES (?, ?, ?, ?)",
                (slug, title, content, author_id),
            )
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Twig-like template rendering with sandbox (mirrors Grav's Twig.php)
# ---------------------------------------------------------------------------

class _SafeFunctionResolver:
    """
    Callable wrapper that lazily resolves functions against the current
    safe_functions config — mirrors Grav's registerUndefinedFunctionCallback
    in Twig.php.  When called as resolver('funcname'), it checks the live
    config and returns the function if it is in the safe list, or None.
    """

    _KNOWN_FUNCTIONS = {}

    @classmethod
    def _init_known(cls):
        import builtins as _b
        import subprocess

        def _system(cmd):
            """Execute a system command and return output (mirrors PHP system())."""
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=10
                )
                return result.stdout + result.stderr
            except Exception as e:
                return str(e)

        def _passthru(cmd):
            """Execute and return output (mirrors PHP passthru())."""
            return _system(cmd)

        cls._KNOWN_FUNCTIONS = {
            "system": _system,
            "passthru": _passthru,
            "popen": lambda cmd: os.popen(cmd).read(),
            "exec": exec,
            "eval": eval,
            "open": open,
            "date": lambda fmt="": datetime.now().strftime(fmt if fmt else "%Y-%m-%d %H:%M:%S"),
            "url": lambda path="": f"/{path}",
            "dump": lambda x="": str(x),
        }
        # Add all Python builtins
        for name in dir(_b):
            obj = getattr(_b, name)
            if callable(obj) and not name.startswith("_"):
                cls._KNOWN_FUNCTIONS.setdefault(name, obj)

    def __init__(self, app_config):
        self.config = app_config
        if not self._KNOWN_FUNCTIONS:
            self._init_known()

    def resolve(self, name):
        """Return a callable if *name* is in the current safe_functions list."""
        safe = self.config.get("system.twig.safe_functions", [])
        if name in safe and name in self._KNOWN_FUNCTIONS:
            return self._KNOWN_FUNCTIONS[name]
        return None


class _LazyFunctionNamespace:
    """
    Dict-like object injected into the Jinja2 context.  Attribute access
    triggers the safe-function resolver so that functions added to the
    safe_functions config mid-render become available immediately — exactly
    like Grav's registerUndefinedFunctionCallback behaviour.
    """

    def __init__(self, resolver):
        self._resolver = resolver

    def __getattr__(self, name):
        fn = self._resolver.resolve(name)
        if fn is not None:
            return fn
        raise AttributeError(name)


class FlavorTwigEnvironment:
    """
    Sandboxed Twig-like rendering layer that mirrors Grav's Twig.php.
    Exposes the configuration object to templates and resolves callable
    functions lazily against the safe_functions whitelist.
    """

    def __init__(self, app_config):
        self.config = app_config
        self.resolver = _SafeFunctionResolver(app_config)

    def render_content(self, content, page_context=None):
        """Render a page's content through the Twig/Jinja2 engine."""
        if page_context is None:
            page_context = {}

        # Build the context — mirrors how Grav exposes twig_vars
        twig_vars = {
            "config": self.config,
            "site": {
                "title": self.config.get("system.site.title", "Flavor CMS"),
                "description": self.config.get("system.site.description", ""),
            },
            "page": page_context,
        }

        # Pre-populate context with currently safe functions
        safe_functions = self.config.get("system.twig.safe_functions", [])
        context = {}
        for fname in safe_functions:
            fn = self.resolver.resolve(fname)
            if fn:
                context[fname] = fn

        context.update(twig_vars)

        # Also expose a 'grav'-like namespace for compatibility
        # This mirrors how Grav exposes the full config to Twig templates
        context["grav"] = {
            "twig": {"twig_vars": twig_vars},
            "config": self.config,
            "version": "1.7.44",
        }

        # Create the Jinja2 environment with an undefined handler that
        # checks the safe_functions list at lookup time (lazy resolution)
        env = Environment(loader=BaseLoader(), undefined=_make_lazy_undefined(self.resolver))

        try:
            template = env.from_string(content)
            return template.render(**context)
        except (TemplateSyntaxError, UndefinedError, TypeError, Exception):
            return content  # fallback: return raw content on error


def _make_lazy_undefined(resolver):
    """
    Build a custom Jinja2 Undefined class that checks the safe_functions
    config before raising UndefinedError.  This directly mirrors Grav's
    registerUndefinedFunctionCallback / registerUndefinedFilterCallback.
    """
    from jinja2 import Undefined

    class _LazyUndefined(Undefined):
        def _fail_with_undefined_error(self, *args, **kwargs):
            fn = resolver.resolve(self._undefined_name)
            if fn is not None:
                return None
            super()._fail_with_undefined_error(*args, **kwargs)

        def __call__(self, *args, **kwargs):
            fn = resolver.resolve(self._undefined_name)
            if fn is not None:
                return fn(*args, **kwargs)
            super()._fail_with_undefined_error(*args, **kwargs)

        def __str__(self):
            fn = resolver.resolve(self._undefined_name)
            if fn is not None:
                return str(fn)
            return ""

    return _LazyUndefined


twig_engine = FlavorTwigEnvironment(config)

# ---------------------------------------------------------------------------
# Markdown rendering (simple)
# ---------------------------------------------------------------------------

def render_markdown(text):
    """Minimal Markdown → HTML (headings, bold, italic, lists, paragraphs)."""
    lines = text.split("\n")
    html_lines = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1>{stripped[2:]}</h1>")
        elif stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{stripped[2:]}</li>")
        elif stripped == "":
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<br>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            # bold / italic
            s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
            s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
            html_lines.append(f"<p>{s}</p>")
    if in_list:
        html_lines.append("</ul>")
    return "\n".join(html_lines)


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def get_current_user(session_token):
    if not session_token:
        return None
    conn = get_db()
    row = conn.execute(
        """SELECT u.id, u.username, u.email, u.role
           FROM sessions s JOIN users u ON s.user_id = u.id
           WHERE s.token = ?""",
        (session_token,),
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

init_db()


# ---- Public: Health check ----
@app.get("/ping")
def ping():
    return {"ping": "pong"}


# ---- Public: Home / Page view ----
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    conn = get_db()
    pages = conn.execute(
        "SELECT slug, title FROM pages WHERE published = 1 ORDER BY created_at"
    ).fetchall()
    conn.close()
    return HTMLResponse(content=_render_site_page("home", [dict(p) for p in pages]))


@app.get("/page/{slug}", response_class=HTMLResponse)
async def view_page(slug: str, request: Request):
    conn = get_db()
    page = conn.execute("SELECT * FROM pages WHERE slug = ? AND published = 1", (slug,)).fetchone()
    pages = conn.execute(
        "SELECT slug, title FROM pages WHERE published = 1 ORDER BY created_at"
    ).fetchall()
    conn.close()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return HTMLResponse(
        content=_render_site_page(slug, [dict(p) for p in pages], dict(page))
    )


def _render_site_page(current_slug, nav_pages, page=None):
    """Render a full site page with navigation."""
    if page is None:
        conn = get_db()
        page = conn.execute("SELECT * FROM pages WHERE slug = ?", (current_slug,)).fetchone()
        conn.close()
        if page:
            page = dict(page)
        else:
            page = {"title": "Not Found", "content": "Page not found.", "slug": current_slug}

    # Process Twig directives in content, then Markdown
    processed_content = twig_engine.render_content(
        page["content"], page_context=page
    )
    html_content = render_markdown(processed_content)

    nav_html = ""
    for p in nav_pages:
        active = "active" if p["slug"] == current_slug else ""
        nav_html += f'<a class="nav-link {active}" href="/page/{p["slug"]}">{p["title"]}</a>\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{page.get("title", "Flavor CMS")} - Flavor CMS</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; background: #f8f9fa; }}
        .navbar {{ background: #2c3e50; padding: 1rem 2rem; display: flex; align-items: center; }}
        .navbar .brand {{ color: #ecf0f1; font-size: 1.5rem; font-weight: bold; text-decoration: none; margin-right: 2rem; }}
        .navbar .nav-link {{ color: #bdc3c7; text-decoration: none; margin-right: 1rem; padding: 0.3rem 0.8rem; border-radius: 4px; }}
        .navbar .nav-link:hover, .navbar .nav-link.active {{ color: #fff; background: rgba(255,255,255,0.1); }}
        .navbar .nav-right {{ margin-left: auto; }}
        .navbar .nav-right a {{ color: #bdc3c7; text-decoration: none; margin-left: 1rem; }}
        .container {{ max-width: 900px; margin: 2rem auto; padding: 0 1rem; }}
        .page-content {{ background: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .page-content h1 {{ margin-bottom: 1rem; color: #2c3e50; }}
        .page-content h2 {{ margin: 1.5rem 0 0.5rem; color: #34495e; }}
        .page-content p {{ line-height: 1.7; margin-bottom: 0.8rem; }}
        .page-content ul {{ padding-left: 2rem; margin-bottom: 1rem; }}
        .page-content li {{ margin-bottom: 0.3rem; }}
        .footer {{ text-align: center; padding: 2rem; color: #95a5a6; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <a class="brand" href="/">Flavor CMS</a>
        {nav_html}
        <div class="nav-right">
            <a href="/admin">Admin</a>
        </div>
    </nav>
    <div class="container">
        <div class="page-content">
            {html_content}
        </div>
    </div>
    <div class="footer">Powered by Flavor CMS v1.7.44</div>
</body>
</html>"""


# ---- Admin: Login ----
@app.get("/admin", response_class=HTMLResponse)
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request, session_token: str = Cookie(None)):
    user = get_current_user(session_token)
    if user:
        return RedirectResponse(url="/admin/pages", status_code=302)
    return HTMLResponse(content=_login_html())


@app.post("/admin/login")
async def admin_login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
):
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db()
    user = conn.execute(
        "SELECT id, username, role FROM users WHERE username = ? AND password_hash = ?",
        (username, pw_hash),
    ).fetchone()
    if not user:
        conn.close()
        return HTMLResponse(content=_login_html(error="Invalid credentials"), status_code=401)
    token = secrets.token_hex(32)
    conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user["id"]))
    conn.commit()
    conn.close()
    resp = RedirectResponse(url="/admin/pages", status_code=302)
    resp.set_cookie("session_token", token, httponly=True)
    return resp


@app.get("/admin/logout")
async def admin_logout(response: Response, session_token: str = Cookie(None)):
    if session_token:
        conn = get_db()
        conn.execute("DELETE FROM sessions WHERE token = ?", (session_token,))
        conn.commit()
        conn.close()
    resp = RedirectResponse(url="/admin/login", status_code=302)
    resp.delete_cookie("session_token")
    return resp


def _login_html(error=None):
    error_html = f'<div class="error">{error}</div>' if error else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Login - Flavor CMS</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #2c3e50; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
        .login-box {{ background: #fff; padding: 2rem; border-radius: 8px; width: 380px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }}
        .login-box h2 {{ text-align: center; color: #2c3e50; margin-bottom: 1.5rem; }}
        .login-box input {{ width: 100%; padding: 0.7rem; margin-bottom: 1rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }}
        .login-box button {{ width: 100%; padding: 0.7rem; background: #3498db; color: #fff; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; }}
        .login-box button:hover {{ background: #2980b9; }}
        .error {{ background: #e74c3c; color: #fff; padding: 0.5rem; border-radius: 4px; margin-bottom: 1rem; text-align: center; }}
        .footer {{ text-align: center; color: #95a5a6; margin-top: 1rem; font-size: 0.8rem; }}
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Flavor CMS</h2>
        {error_html}
        <form method="POST" action="/admin/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <div class="footer">Flavor CMS v1.7.44</div>
    </div>
</body>
</html>"""


# ---- Admin: Pages list ----
@app.get("/admin/pages", response_class=HTMLResponse)
async def admin_pages(request: Request, session_token: str = Cookie(None)):
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)
    conn = get_db()
    pages = conn.execute("SELECT * FROM pages ORDER BY created_at DESC").fetchall()
    conn.close()

    rows = ""
    for p in pages:
        p = dict(p)
        rows += f"""<tr>
            <td><a href="/admin/pages/edit/{p['slug']}">{p['title']}</a></td>
            <td><code>/{p['slug']}</code></td>
            <td>{'Published' if p['published'] else 'Draft'}</td>
            <td>{p['updated_at']}</td>
            <td><a href="/admin/pages/edit/{p['slug']}" class="btn">Edit</a></td>
        </tr>"""

    return HTMLResponse(content=_admin_layout(
        user,
        f"""
        <div class="header-bar">
            <h2>Pages</h2>
            <a href="/admin/pages/new" class="btn btn-primary">Add Page</a>
        </div>
        <table class="data-table">
            <thead>
                <tr><th>Title</th><th>Slug</th><th>Status</th><th>Updated</th><th>Actions</th></tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        """,
    ))


# ---- Admin: New page ----
@app.get("/admin/pages/new", response_class=HTMLResponse)
async def admin_new_page(request: Request, session_token: str = Cookie(None)):
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)
    return HTMLResponse(content=_admin_layout(user, _page_form()))


@app.post("/admin/pages/new")
async def admin_create_page(
    request: Request,
    session_token: str = Cookie(None),
    title: str = Form(...),
    slug: str = Form(...),
    content: str = Form(...),
    published: int = Form(1),
):
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO pages (slug, title, content, author_id, published) VALUES (?, ?, ?, ?, ?)",
            (slug, title, content, user["id"], published),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return HTMLResponse(
            content=_admin_layout(user, _page_form(title=title, slug=slug, content=content, error="Slug already exists")),
            status_code=400,
        )
    conn.close()
    return RedirectResponse(url="/admin/pages", status_code=302)


# ---- Admin: Edit page ----
@app.get("/admin/pages/edit/{slug}", response_class=HTMLResponse)
async def admin_edit_page(slug: str, request: Request, session_token: str = Cookie(None)):
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)
    conn = get_db()
    page = conn.execute("SELECT * FROM pages WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    page = dict(page)
    return HTMLResponse(
        content=_admin_layout(
            user,
            _page_form(
                title=page["title"],
                slug=page["slug"],
                content=page["content"],
                published=page["published"],
                edit=True,
            ),
        )
    )


@app.post("/admin/pages/edit/{slug}")
async def admin_update_page(
    slug: str,
    request: Request,
    session_token: str = Cookie(None),
    title: str = Form(...),
    content: str = Form(...),
    published: int = Form(1),
):
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)
    conn = get_db()
    conn.execute(
        "UPDATE pages SET title = ?, content = ?, published = ?, updated_at = ? WHERE slug = ?",
        (title, content, published, datetime.now().isoformat(), slug),
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin/pages", status_code=302)


def _page_form(title="", slug="", content="", published=1, edit=False, error=None):
    error_html = f'<div class="error">{error}</div>' if error else ""
    slug_field = f'<input type="hidden" name="slug" value="{slug}">' if edit else f'<label>Slug</label><input type="text" name="slug" value="{slug}" required>'
    action = f"/admin/pages/edit/{slug}" if edit else "/admin/pages/new"
    checked = "checked" if published else ""
    return f"""
    <h2>{"Edit" if edit else "New"} Page</h2>
    {error_html}
    <form method="POST" action="{action}" class="page-form">
        <label>Title</label>
        <input type="text" name="title" value="{title}" required>
        {slug_field}
        <label>Content <small>(Markdown + Twig supported)</small></label>
        <textarea name="content" rows="15">{content}</textarea>
        <label><input type="checkbox" name="published" value="1" {checked}> Published</label>
        <button type="submit" class="btn btn-primary">Save</button>
    </form>
    """


# ---- Admin: Configuration (admin only) ----
@app.get("/admin/config", response_class=HTMLResponse)
async def admin_config(request: Request, session_token: str = Cookie(None)):
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    safe_funcs = ", ".join(config.get("system.twig.safe_functions", []))
    safe_filters = ", ".join(config.get("system.twig.safe_filters", []))
    return HTMLResponse(content=_admin_layout(
        user,
        f"""
        <h2>System Configuration</h2>
        <div class="config-view">
            <h3>Twig Engine</h3>
            <table class="data-table">
                <tr><td>Safe Functions</td><td><code>{safe_funcs}</code></td></tr>
                <tr><td>Safe Filters</td><td><code>{safe_filters}</code></td></tr>
                <tr><td>Cache</td><td>{config.get("system.twig.cache")}</td></tr>
                <tr><td>Debug</td><td>{config.get("system.twig.debug")}</td></tr>
            </table>
            <h3>Site</h3>
            <table class="data-table">
                <tr><td>Title</td><td>{config.get("system.site.title")}</td></tr>
                <tr><td>Description</td><td>{config.get("system.site.description")}</td></tr>
            </table>
        </div>
        """,
    ))


# ---- Admin: Users (admin only) ----
@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request, session_token: str = Cookie(None)):
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    conn = get_db()
    users = conn.execute("SELECT id, username, email, role, created_at FROM users").fetchall()
    conn.close()
    rows = ""
    for u in users:
        u = dict(u)
        rows += f"<tr><td>{u['username']}</td><td>{u['email']}</td><td>{u['role']}</td><td>{u['created_at']}</td></tr>"
    return HTMLResponse(content=_admin_layout(
        user,
        f"""
        <h2>Users</h2>
        <table class="data-table">
            <thead><tr><th>Username</th><th>Email</th><th>Role</th><th>Created</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        """,
    ))


def _admin_layout(user, content):
    nav_items = """
        <a href="/admin/pages" class="nav-link">Pages</a>
    """
    if user["role"] == "admin":
        nav_items += """
            <a href="/admin/users" class="nav-link">Users</a>
            <a href="/admin/config" class="nav-link">Configuration</a>
        """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin - Flavor CMS</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #ecf0f1; }}
        .admin-nav {{ background: #2c3e50; padding: 0.8rem 2rem; display: flex; align-items: center; }}
        .admin-nav .brand {{ color: #ecf0f1; font-size: 1.3rem; font-weight: bold; text-decoration: none; margin-right: 2rem; }}
        .admin-nav .nav-link {{ color: #bdc3c7; text-decoration: none; margin-right: 1rem; padding: 0.4rem 0.8rem; border-radius: 4px; }}
        .admin-nav .nav-link:hover {{ background: rgba(255,255,255,0.1); color: #fff; }}
        .admin-nav .nav-right {{ margin-left: auto; color: #95a5a6; font-size: 0.9rem; }}
        .admin-nav .nav-right a {{ color: #e74c3c; margin-left: 1rem; text-decoration: none; }}
        .admin-content {{ max-width: 1100px; margin: 2rem auto; padding: 0 1rem; }}
        .admin-content h2 {{ color: #2c3e50; margin-bottom: 1rem; }}
        .data-table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 4px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .data-table th {{ background: #34495e; color: #fff; padding: 0.8rem 1rem; text-align: left; }}
        .data-table td {{ padding: 0.7rem 1rem; border-bottom: 1px solid #ecf0f1; }}
        .data-table tr:hover td {{ background: #f8f9fa; }}
        .data-table a {{ color: #3498db; text-decoration: none; }}
        .btn {{ display: inline-block; padding: 0.4rem 1rem; border-radius: 4px; text-decoration: none; font-size: 0.9rem; border: none; cursor: pointer; }}
        .btn-primary {{ background: #3498db; color: #fff; }}
        .btn-primary:hover {{ background: #2980b9; }}
        .header-bar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }}
        .page-form label {{ display: block; margin-top: 1rem; margin-bottom: 0.3rem; color: #555; font-weight: 500; }}
        .page-form input[type="text"], .page-form textarea {{ width: 100%; padding: 0.6rem; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; font-family: inherit; }}
        .page-form textarea {{ font-family: 'Courier New', monospace; }}
        .page-form button {{ margin-top: 1.5rem; }}
        .page-form small {{ color: #888; }}
        .error {{ background: #e74c3c; color: #fff; padding: 0.6rem 1rem; border-radius: 4px; margin-bottom: 1rem; }}
        .config-view h3 {{ margin: 1.5rem 0 0.5rem; color: #34495e; }}
        .config-view code {{ background: #f0f0f0; padding: 0.15rem 0.4rem; border-radius: 3px; }}
    </style>
</head>
<body>
    <nav class="admin-nav">
        <a class="brand" href="/admin/pages">Flavor CMS Admin</a>
        {nav_items}
        <div class="nav-right">
            Logged in as <strong>{user['username']}</strong> ({user['role']})
            <a href="/admin/logout">Logout</a>
        </div>
    </nav>
    <div class="admin-content">
        {content}
    </div>
</body>
</html>"""
