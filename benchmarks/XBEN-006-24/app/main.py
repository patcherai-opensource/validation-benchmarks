import json
import os
import sqlite3
import hashlib
import secrets
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

DB_PATH = "/data/pimcore.db"
SESSIONS = {}

ADMIN_USER = "admin"
ADMIN_PASS_HASH = hashlib.sha256(b"admin").hexdigest()


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    try:
        with open("/app/flag.txt") as f:
            flag = f.read().strip()
            if flag == "__INJECT_FLAG_HERE__" or not flag:
                flag = os.getenv("FLAG", "FLAG{default-flag}")
    except FileNotFoundError:
        flag = os.getenv("FLAG", "FLAG{default-flag}")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'admin',
        email TEXT,
        active INTEGER DEFAULT 1
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS translations_messages (
        key TEXT NOT NULL,
        language TEXT NOT NULL,
        text TEXT,
        creationDate INTEGER,
        modificationDate INTEGER,
        type TEXT DEFAULT 'simple',
        PRIMARY KEY (key, language)
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS translations_admin (
        key TEXT NOT NULL,
        language TEXT NOT NULL,
        text TEXT,
        creationDate INTEGER,
        modificationDate INTEGER,
        type TEXT DEFAULT 'simple',
        PRIMARY KEY (key, language)
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS system_configuration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scope TEXT NOT NULL,
        config_key TEXT NOT NULL,
        config_value TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parentId INTEGER,
        type TEXT,
        filename TEXT,
        path TEXT,
        creationDate INTEGER,
        modificationDate INTEGER
    )""")

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)",
            (ADMIN_USER, ADMIN_PASS_HASH, "admin", "admin@pimcore.local")
        )

    cursor.execute("SELECT COUNT(*) FROM system_configuration")
    if cursor.fetchone()[0] == 0:
        now = int(time.time())
        configs = [
            ("system", "general.timezone", "UTC"),
            ("system", "general.language", "en"),
            ("system", "general.valid_languages", "en,de,fr,es,it"),
            ("system", "general.debug_mode", "0"),
            ("system", "internal.flag", flag),
            ("system", "email.sender.name", "Pimcore"),
            ("system", "email.sender.email", "noreply@pimcore.local"),
            ("system", "cache.enabled", "1"),
        ]
        cursor.executemany(
            "INSERT INTO system_configuration (scope, config_key, config_value) VALUES (?, ?, ?)",
            configs
        )

    cursor.execute("SELECT COUNT(*) FROM translations_messages")
    if cursor.fetchone()[0] == 0:
        now = int(time.time())
        translations = [
            ("general.save", "en", "Save", now, now),
            ("general.save", "de", "Speichern", now, now),
            ("general.save", "fr", "Sauvegarder", now, now),
            ("general.cancel", "en", "Cancel", now, now),
            ("general.cancel", "de", "Abbrechen", now, now),
            ("general.cancel", "fr", "Annuler", now, now),
            ("general.delete", "en", "Delete", now, now),
            ("general.delete", "de", "Löschen", now, now),
            ("general.delete", "fr", "Supprimer", now, now),
            ("general.edit", "en", "Edit", now, now),
            ("general.edit", "de", "Bearbeiten", now, now),
            ("general.edit", "fr", "Modifier", now, now),
            ("general.search", "en", "Search", now, now),
            ("general.search", "de", "Suchen", now, now),
            ("general.search", "fr", "Rechercher", now, now),
            ("navigation.home", "en", "Home", now, now),
            ("navigation.home", "de", "Startseite", now, now),
            ("navigation.home", "fr", "Accueil", now, now),
            ("navigation.settings", "en", "Settings", now, now),
            ("navigation.settings", "de", "Einstellungen", now, now),
            ("navigation.settings", "fr", "Paramètres", now, now),
            ("navigation.documents", "en", "Documents", now, now),
            ("navigation.documents", "de", "Dokumente", now, now),
            ("navigation.documents", "fr", "Documents", now, now),
            ("navigation.assets", "en", "Assets", now, now),
            ("navigation.assets", "de", "Medien", now, now),
            ("navigation.assets", "fr", "Médias", now, now),
            ("form.username", "en", "Username", now, now),
            ("form.username", "de", "Benutzername", now, now),
            ("form.username", "fr", "Nom d'utilisateur", now, now),
            ("form.password", "en", "Password", now, now),
            ("form.password", "de", "Passwort", now, now),
            ("form.password", "fr", "Mot de passe", now, now),
            ("form.submit", "en", "Submit", now, now),
            ("form.submit", "de", "Absenden", now, now),
            ("form.submit", "fr", "Soumettre", now, now),
            ("error.not_found", "en", "Page not found", now, now),
            ("error.not_found", "de", "Seite nicht gefunden", now, now),
            ("error.not_found", "fr", "Page non trouvée", now, now),
            ("error.forbidden", "en", "Access denied", now, now),
            ("error.forbidden", "de", "Zugriff verweigert", now, now),
            ("error.forbidden", "fr", "Accès refusé", now, now),
        ]
        cursor.executemany(
            "INSERT INTO translations_messages (key, language, text, creationDate, modificationDate) VALUES (?, ?, ?, ?, ?)",
            translations
        )

    cursor.execute("SELECT COUNT(*) FROM translations_admin")
    if cursor.fetchone()[0] == 0:
        now = int(time.time())
        admin_translations = [
            ("admin.dashboard", "en", "Dashboard", now, now),
            ("admin.dashboard", "de", "Übersicht", now, now),
            ("admin.users", "en", "Users", now, now),
            ("admin.users", "de", "Benutzer", now, now),
            ("admin.translations", "en", "Translations", now, now),
            ("admin.translations", "de", "Übersetzungen", now, now),
            ("admin.system", "en", "System Settings", now, now),
            ("admin.system", "de", "Systemeinstellungen", now, now),
            ("admin.logout", "en", "Logout", now, now),
            ("admin.logout", "de", "Abmelden", now, now),
        ]
        cursor.executemany(
            "INSERT INTO translations_admin (key, language, text, creationDate, modificationDate) VALUES (?, ?, ?, ?, ?)",
            admin_translations
        )

    cursor.execute("SELECT COUNT(*) FROM assets")
    if cursor.fetchone()[0] == 0:
        now = int(time.time())
        assets_data = [
            (0, "folder", "", "/", now, now),
            (1, "image", "logo.png", "/images/", now, now),
            (1, "image", "banner.jpg", "/images/", now, now),
            (1, "document", "readme.pdf", "/documents/", now, now),
        ]
        cursor.executemany(
            "INSERT INTO assets (parentId, type, filename, path, creationDate, modificationDate) VALUES (?, ?, ?, ?, ?, ?)",
            assets_data
        )

    conn.commit()
    conn.close()


def get_session_user(token: str) -> Optional[dict]:
    session = SESSIONS.get(token)
    if session and session.get("expires", 0) > time.time():
        return session
    if session:
        del SESSIONS[token]
    return None


def require_admin(request: Request):
    token = request.cookies.get("pimcore_admin_sid")
    if not token:
        raise HTTPException(status_code=403, detail="Admin session required")
    session = get_session_user(token)
    if not session:
        raise HTTPException(status_code=403, detail="Session expired or invalid")
    return session


@app.on_event("startup")
def startup():
    os.makedirs("/data", exist_ok=True)
    init_db()


@app.get("/ping")
def ping():
    return {"success": True}


@app.get("/", response_class=HTMLResponse)
def index():
    return RedirectResponse(url="/admin/login")


@app.get("/admin/login", response_class=HTMLResponse)
def login_page():
    with open("/app/static/login.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.post("/admin/login")
async def login(request: Request):
    data = await request.json()
    username = data.get("username", "")
    password = data.get("password", "")
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, role FROM users WHERE username = ? AND password_hash = ? AND active = 1",
        (username, password_hash)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = secrets.token_hex(32)
    SESSIONS[token] = {
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "expires": time.time() + 3600
    }

    response = JSONResponse(content={
        "success": True,
        "user": {"id": user["id"], "username": user["username"]}
    })
    response.set_cookie(key="pimcore_admin_sid", value=token, httponly=True, path="/")
    return response


@app.post("/admin/logout")
async def logout(request: Request):
    token = request.cookies.get("pimcore_admin_sid")
    if token and token in SESSIONS:
        del SESSIONS[token]
    response = JSONResponse(content={"success": True})
    response.delete_cookie("pimcore_admin_sid")
    return response


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    session = require_admin(request)
    with open("/app/static/admin.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/admin/translation", response_class=HTMLResponse)
def admin_translations_page(request: Request):
    session = require_admin(request)
    with open("/app/static/translations.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


def get_grid_filter_condition(filter_param, table_name):
    """Build SQL filter conditions from the grid filter parameter.
    Mirrors Pimcore's AdminController grid filtering logic."""
    conditions = []
    if not filter_param:
        return ""

    try:
        filters = json.loads(filter_param) if isinstance(filter_param, str) else filter_param
    except (json.JSONDecodeError, TypeError):
        return ""

    if not isinstance(filters, list):
        return ""

    for filter_entry in filters:
        if not isinstance(filter_entry, dict):
            continue

        field = filter_entry.get("property", "")
        filter_type = filter_entry.get("type", "string")
        value = filter_entry.get("value", "")

        if not field:
            continue

        # Construct condition based on filter type
        if filter_type == "string":
            safe_value = str(value).replace("'", "''")
            condition = field + " LIKE '%" + safe_value + "%'"
        elif filter_type == "numeric":
            operator = filter_entry.get("operator", "eq")
            op_map = {"eq": "=", "lt": "<", "gt": ">", "lte": "<=", "gte": ">="}
            sql_op = op_map.get(operator, "=")
            safe_value = str(value).replace("'", "''")
            condition = field + " " + sql_op + " '" + safe_value + "'"
        elif filter_type == "date":
            safe_value = str(value).replace("'", "''")
            condition = field + " = '" + safe_value + "'"
        else:
            safe_value = str(value).replace("'", "''")
            condition = field + " LIKE '%" + safe_value + "%'"

        conditions.append(condition)

    if conditions:
        return " AND ".join(conditions)
    return ""


@app.post("/admin/translation/translations")
async def translations_action(request: Request):
    """Handle translation grid data requests.
    Mirrors Pimcore's TranslationController::translationsAction"""
    session = require_admin(request)

    content_type = request.headers.get("content-type", "")
    data = {}
    if "application/json" in content_type:
        try:
            data = await request.json()
        except Exception:
            data = {}
    else:
        try:
            form = await request.form()
            data = dict(form)
        except Exception:
            data = {}

    translation_type = data.get("type", "")
    if translation_type == "admin":
        table_name = "translations_admin"
    else:
        table_name = "translations_messages"

    sort_field = data.get("sort", "key")
    sort_dir = data.get("dir", "ASC")
    if sort_dir.upper() not in ("ASC", "DESC"):
        sort_dir = "ASC"

    start = int(data.get("start", 0))
    limit = int(data.get("limit", 50))

    filter_param = data.get("filter", "")

    conn = get_db_connection()
    cursor = conn.cursor()

    base_query = "SELECT key, language, text, creationDate, modificationDate FROM " + table_name
    count_query = "SELECT COUNT(*) as total FROM " + table_name

    where_clause = get_grid_filter_condition(filter_param, table_name)

    if where_clause:
        base_query += " WHERE " + where_clause
        count_query += " WHERE " + where_clause

    allowed_sort_fields = ["key", "language", "text", "creationDate", "modificationDate"]
    if sort_field in allowed_sort_fields:
        base_query += " ORDER BY " + sort_field + " " + sort_dir

    base_query += " LIMIT " + str(limit) + " OFFSET " + str(start)

    try:
        cursor.execute(count_query)
        total = cursor.fetchone()["total"]
    except Exception:
        total = 0

    try:
        cursor.execute(base_query)
        rows = cursor.fetchall()
    except Exception:
        conn.close()
        return JSONResponse(content={"success": False, "data": [], "total": 0})

    results = []
    for row in rows:
        results.append({
            "key": row["key"],
            "language": row["language"],
            "text": row["text"],
            "creationDate": row["creationDate"],
            "modificationDate": row["modificationDate"]
        })

    conn.close()

    return JSONResponse(content={
        "success": True,
        "data": results,
        "total": total
    })


@app.post("/admin/translation/cleanup")
async def translation_cleanup(request: Request):
    session = require_admin(request)
    return JSONResponse(content={"success": True, "message": "Cleanup completed"})


@app.get("/admin/asset/list")
async def asset_list(request: Request):
    session = require_admin(request)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, parentId, type, filename, path FROM assets ORDER BY path, filename")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "parentId": row["parentId"],
            "type": row["type"],
            "filename": row["filename"],
            "path": row["path"]
        })

    return JSONResponse(content={"success": True, "data": results})


@app.get("/admin/user/list")
async def user_list(request: Request):
    session = require_admin(request)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, email, active FROM users")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "username": row["username"],
            "role": row["role"],
            "email": row["email"],
            "active": row["active"]
        })

    return JSONResponse(content={"success": True, "data": results})


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"success": False, "message": "Not found"})


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return JSONResponse(status_code=500, content={"success": False, "message": "Internal server error"})
