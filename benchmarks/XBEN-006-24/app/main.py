import json
import os
import sqlite3
import hashlib
import secrets
import time

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

DB_PATH = "/app/data/cms.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.on_event("startup")
def init_database():
    os.makedirs("/app/data", exist_ok=True)

    try:
        with open("flag.txt") as f:
            flag = f.read().strip()
            if flag == "FLAG":
                flag = "FLAG{missing-flag}"
    except FileNotFoundError:
        flag = "FLAG{missing-flag}"

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'editor',
        active INTEGER DEFAULT 1,
        created_at INTEGER
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL,
        language TEXT NOT NULL,
        text TEXT,
        domain TEXT DEFAULT 'messages',
        type TEXT DEFAULT 'simple',
        creationDate INTEGER,
        modificationDate INTEGER
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS system_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scope TEXT NOT NULL,
        name TEXT NOT NULL,
        value TEXT
    )""")

    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM translations")
    cursor.execute("DELETE FROM system_settings")

    admin_pass = hash_password("cms_admin_2024!")
    editor_pass = hash_password("editor")
    now = int(time.time())

    cursor.execute(
        "INSERT INTO users (username, password, role, active, created_at) VALUES (?, ?, ?, ?, ?)",
        ("admin", admin_pass, "admin", 1, now)
    )
    cursor.execute(
        "INSERT INTO users (username, password, role, active, created_at) VALUES (?, ?, ?, ?, ?)",
        ("editor", editor_pass, "editor", 1, now)
    )

    translations_data = [
        ("homepage.title", "en", "Welcome to our platform", "messages", "simple", now, now),
        ("homepage.title", "de", "Willkommen auf unserer Plattform", "messages", "simple", now, now),
        ("homepage.title", "fr", "Bienvenue sur notre plateforme", "messages", "simple", now, now),
        ("homepage.subtitle", "en", "The best content management system", "messages", "simple", now, now),
        ("homepage.subtitle", "de", "Das beste Content-Management-System", "messages", "simple", now, now),
        ("homepage.subtitle", "fr", "Le meilleur système de gestion de contenu", "messages", "simple", now, now),
        ("nav.home", "en", "Home", "messages", "simple", now, now),
        ("nav.home", "de", "Startseite", "messages", "simple", now, now),
        ("nav.home", "fr", "Accueil", "messages", "simple", now, now),
        ("nav.about", "en", "About Us", "messages", "simple", now, now),
        ("nav.about", "de", "Über uns", "messages", "simple", now, now),
        ("nav.about", "fr", "À propos de nous", "messages", "simple", now, now),
        ("nav.contact", "en", "Contact", "messages", "simple", now, now),
        ("nav.contact", "de", "Kontakt", "messages", "simple", now, now),
        ("nav.contact", "fr", "Contact", "messages", "simple", now, now),
        ("footer.copyright", "en", "All rights reserved", "messages", "simple", now, now),
        ("footer.copyright", "de", "Alle Rechte vorbehalten", "messages", "simple", now, now),
        ("footer.copyright", "fr", "Tous droits réservés", "messages", "simple", now, now),
        ("btn.submit", "en", "Submit", "messages", "simple", now, now),
        ("btn.submit", "de", "Absenden", "messages", "simple", now, now),
        ("btn.submit", "fr", "Soumettre", "messages", "simple", now, now),
        ("btn.cancel", "en", "Cancel", "messages", "simple", now, now),
        ("btn.cancel", "de", "Abbrechen", "messages", "simple", now, now),
        ("btn.cancel", "fr", "Annuler", "messages", "simple", now, now),
        ("error.notfound", "en", "Page not found", "messages", "simple", now, now),
        ("error.notfound", "de", "Seite nicht gefunden", "messages", "simple", now, now),
        ("error.notfound", "fr", "Page non trouvée", "messages", "simple", now, now),
        ("error.forbidden", "en", "Access denied", "messages", "simple", now, now),
        ("error.forbidden", "de", "Zugriff verweigert", "messages", "simple", now, now),
        ("error.forbidden", "fr", "Accès refusé", "messages", "simple", now, now),
        ("admin.dashboard", "en", "Dashboard", "admin", "simple", now, now),
        ("admin.dashboard", "de", "Übersicht", "admin", "simple", now, now),
        ("admin.settings", "en", "Settings", "admin", "simple", now, now),
        ("admin.settings", "de", "Einstellungen", "admin", "simple", now, now),
        ("admin.users", "en", "User Management", "admin", "simple", now, now),
        ("admin.users", "de", "Benutzerverwaltung", "admin", "simple", now, now),
    ]

    for t in translations_data:
        cursor.execute(
            "INSERT INTO translations (key, language, text, domain, type, creationDate, modificationDate) VALUES (?, ?, ?, ?, ?, ?, ?)",
            t
        )

    settings_data = [
        ("system", "app.name", "ContentPlatform CMS"),
        ("system", "app.version", "4.2.1"),
        ("system", "app.debug", "false"),
        ("system", "app.timezone", "Europe/Berlin"),
        ("email", "smtp.host", "mail.internal.local"),
        ("email", "smtp.port", "587"),
        ("security", "session.lifetime", "3600"),
        ("security", "csrf.enabled", "true"),
        ("internal", "deployment.token", flag),
    ]

    for s in settings_data:
        cursor.execute(
            "INSERT INTO system_settings (scope, name, value) VALUES (?, ?, ?)",
            s
        )

    conn.commit()
    conn.close()


def require_admin(request: Request):
    session_user = request.session.get("user")
    if not session_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return session_user


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/admin/login", response_class=HTMLResponse)
def login_page():
    with open("static/login.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.post("/admin/login")
async def do_login(request: Request):
    data = await request.json()
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return JSONResponse({"success": False, "message": "Missing credentials"}, status_code=400)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, role FROM users WHERE username = ? AND password = ? AND active = 1",
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return JSONResponse({"success": False, "message": "Invalid credentials"}, status_code=401)

    request.session["user"] = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"]
    }
    return JSONResponse({"success": True, "redirect": "/admin/portal"})


@app.post("/admin/logout")
async def do_logout(request: Request):
    request.session.clear()
    return JSONResponse({"success": True})


@app.get("/admin/portal", response_class=HTMLResponse)
def admin_portal(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)
    with open("static/portal.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/admin/api/session")
def session_info(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"authenticated": False}, status_code=401)
    return JSONResponse({"authenticated": True, "user": user})


@app.get("/admin/api/languages")
def get_languages(user=Depends(require_admin)):
    return JSONResponse({
        "languages": ["en", "de", "fr"],
        "default": "en"
    })


@app.get("/admin/api/domains")
def get_domains(user=Depends(require_admin)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT domain FROM translations")
    domains = [row["domain"] for row in cursor.fetchall()]
    conn.close()
    return JSONResponse({"domains": domains})


@app.post("/admin/api/localization/entries")
async def list_entries(request: Request, user=Depends(require_admin)):
    """
    Lists translation entries with optional filtering and pagination.
    Accepts JSON body with: domain, limit, start, filter, searchString, sort, dir
    """
    try:
        data = await request.json()
    except Exception:
        data = {}

    domain = data.get("domain", "messages")
    limit = data.get("limit", 50)
    start = data.get("start", 0)
    sort_field = data.get("sort", "key")
    sort_dir = data.get("dir", "ASC")

    try:
        limit = int(limit)
        start = int(start)
    except (ValueError, TypeError):
        limit = 50
        start = 0

    if limit > 200:
        limit = 200
    if limit < 1:
        limit = 50

    if sort_dir not in ("ASC", "DESC", "asc", "desc"):
        sort_dir = "ASC"

    allowed_sort = ["key", "language", "text", "type", "creationDate", "modificationDate"]
    if sort_field not in allowed_sort:
        sort_field = "key"

    conn = get_db()
    cursor = conn.cursor()

    table_name = "translations"
    conditions = []
    params = []

    conditions.append(f"{table_name}.domain = ?")
    params.append(domain)

    filter_json = data.get("filter")
    if filter_json:
        if isinstance(filter_json, str):
            try:
                filters = json.loads(filter_json)
            except json.JSONDecodeError:
                filters = []
        elif isinstance(filter_json, list):
            filters = filter_json
        else:
            filters = []

        for f in filters:
            if not isinstance(f, dict):
                continue

            fieldname = f.get("property", "")
            filter_type = f.get("type", "string")
            value = f.get("value", "")

            if not fieldname or not value:
                continue

            fieldname = fieldname.replace("--", "")

            if filter_type == "string":
                operator = "LIKE"
                field = fieldname
                value = f"%{value}%"
            elif filter_type == "numeric":
                op_map = {"lt": "<", "gt": ">", "eq": "="}
                operator = op_map.get(f.get("operator", "eq"), "=")
                field = fieldname
            else:
                operator = "LIKE"
                field = fieldname
                value = f"%{value}%"

            condition = f"{field} {operator} '{value}'"
            conditions.append(condition)

    search = data.get("searchString")
    if search:
        search_val = f"%{search.lower()}%"
        conditions.append(f"(lower({table_name}.key) LIKE ? OR lower({table_name}.text) LIKE ?)")
        params.append(search_val)
        params.append(search_val)

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    query = f"SELECT * FROM {table_name} WHERE {where_clause} ORDER BY {sort_field} {sort_dir} LIMIT {limit} OFFSET {start}"

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid filter parameters")

    count_query = f"SELECT COUNT(*) as cnt FROM {table_name} WHERE {where_clause}"
    try:
        cursor.execute(count_query, params)
        total = cursor.fetchone()["cnt"]
    except sqlite3.OperationalError:
        total = 0

    conn.close()

    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "key": row["key"],
            "language": row["language"],
            "text": row["text"],
            "domain": row["domain"],
            "type": row["type"],
            "creationDate": row["creationDate"],
            "modificationDate": row["modificationDate"],
        })

    return JSONResponse({
        "data": results,
        "total": total,
        "success": True
    })


@app.post("/admin/api/localization/update")
async def update_entry(request: Request, user=Depends(require_admin)):
    data = await request.json()
    entry_id = data.get("id")
    text = data.get("text")

    if not entry_id:
        return JSONResponse({"success": False, "message": "Missing entry ID"}, status_code=400)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE translations SET text = ?, modificationDate = ? WHERE id = ?",
        (text, int(time.time()), entry_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()

    if affected == 0:
        return JSONResponse({"success": False, "message": "Entry not found"}, status_code=404)

    return JSONResponse({"success": True})


@app.post("/admin/api/localization/create")
async def create_entry(request: Request, user=Depends(require_admin)):
    data = await request.json()
    key = data.get("key", "")
    language = data.get("language", "en")
    text = data.get("text", "")
    domain = data.get("domain", "messages")

    if not key:
        return JSONResponse({"success": False, "message": "Translation key is required"}, status_code=400)

    now = int(time.time())
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM translations WHERE key = ? AND language = ? AND domain = ?",
        (key, language, domain)
    )
    if cursor.fetchone():
        conn.close()
        return JSONResponse({"success": False, "message": "Translation key already exists for this language"}, status_code=409)

    cursor.execute(
        "INSERT INTO translations (key, language, text, domain, type, creationDate, modificationDate) VALUES (?, ?, ?, ?, 'simple', ?, ?)",
        (key, language, text, domain, now, now)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return JSONResponse({"success": True, "id": new_id})


@app.delete("/admin/api/localization/delete")
async def delete_entry(request: Request, user=Depends(require_admin)):
    data = await request.json()
    entry_id = data.get("id")

    if not entry_id:
        return JSONResponse({"success": False, "message": "Missing entry ID"}, status_code=400)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM translations WHERE id = ?", (entry_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()

    if affected == 0:
        return JSONResponse({"success": False, "message": "Entry not found"}, status_code=404)

    return JSONResponse({"success": True})


@app.get("/admin/api/settings")
def get_settings(user=Depends(require_admin)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT scope, name, value FROM system_settings WHERE scope != 'internal'")
    rows = cursor.fetchall()
    conn.close()

    settings = {}
    for row in rows:
        scope = row["scope"]
        if scope not in settings:
            settings[scope] = {}
        settings[scope][row["name"]] = row["value"]

    return JSONResponse({"settings": settings})

