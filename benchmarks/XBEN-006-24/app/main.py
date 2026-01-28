import json
import os
import re

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import sqlite3

app = FastAPI(title="Pimcore Object Manager", version="2.1.3")


def get_db_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.on_event("startup")
def startup():
    # Try to read flag from file, fallback to environment variable
    try:
        with open("flag.txt") as f:
            flag = f.read().strip()
            # If flag.txt still contains placeholder, try environment
            if flag == "FLAG":
                flag = os.getenv("FLAG", "FLAG{default-flag}")
    except FileNotFoundError:
        flag = os.getenv("FLAG", "FLAG{default-flag}")

    conn = get_db_connection()
    
    # Products table - main data objects
    conn.execute('''CREATE TABLE IF NOT EXISTS products (
        o_id INTEGER PRIMARY KEY,
        o_key TEXT,
        o_classId TEXT,
        o_type TEXT,
        name TEXT,
        sku TEXT,
        tags TEXT,
        price REAL,
        status TEXT
    )''')
    
    # Users table for privilege escalation theme
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password_hash TEXT,
        admin INTEGER DEFAULT 0,
        notes TEXT
    )''')
    
    # Audit log - noise table
    conn.execute('''CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY,
        action TEXT,
        timestamp TEXT,
        user_id INTEGER
    )''')
    
    conn.execute('DELETE FROM products')
    conn.execute('DELETE FROM users')
    conn.execute('DELETE FROM audit_log')
    
    # Insert product data
    conn.execute('''INSERT INTO products (o_key, o_classId, o_type, name, sku, tags, price, status) VALUES 
        ("laptop-pro", "Product", "object", "Laptop Pro 15", "SKU-001", "electronics,computers,featured", 1299.99, "published"),
        ("wireless-mouse", "Product", "object", "Wireless Mouse", "SKU-002", "electronics,accessories", 29.99, "published"),
        ("usb-hub", "Product", "object", "USB-C Hub 7-Port", "SKU-003", "electronics,accessories,usb", 49.99, "published"),
        ("monitor-27", "Product", "object", "27 inch Monitor", "SKU-004", "electronics,displays,featured", 399.99, "published"),
        ("keyboard-mech", "Product", "object", "Mechanical Keyboard", "SKU-005", "electronics,accessories,gaming", 149.99, "draft"),
        ("webcam-hd", "Product", "object", "HD Webcam 1080p", "SKU-006", "electronics,video,work-from-home", 79.99, "published"),
        ("headphones", "Product", "object", "Noise Cancelling Headphones", "SKU-007", "electronics,audio,featured", 249.99, "published"),
        ("tablet-10", "Product", "object", "Tablet 10 inch", "SKU-008", "electronics,mobile,featured", 449.99, "draft")
    ''')
    
    # Insert users - flag is in admin notes
    conn.execute(f'''INSERT INTO users (username, password_hash, admin, notes) VALUES 
        ("viewer", "5f4dcc3b5aa765d61d8327deb882cf99", 0, "Read-only access user"),
        ("editor", "098f6bcd4621d373cade4e832627b4f6", 0, "Content editor"),
        ("system", "d033e22ae348aeb5660fc2140aec35850c4da997", 1, "{flag}")
    ''')
    
    # Audit log entries
    conn.execute('''INSERT INTO audit_log (action, timestamp, user_id) VALUES 
        ("login", "2024-01-15T09:30:00Z", 1),
        ("product_update", "2024-01-15T10:15:00Z", 2),
        ("login", "2024-01-15T11:00:00Z", 2),
        ("product_create", "2024-01-15T14:30:00Z", 2)
    ''')
    
    conn.commit()
    conn.close()


# Main vulnerable endpoint - mimics Pimcore's grid-proxy
@app.post("/admin/object/grid-proxy")
async def grid_proxy(request: Request, classId: str = Query(default="Product")):
    """
    Grid proxy endpoint for filtering data objects.
    Accepts filter parameter in JSON format similar to Pimcore.
    """
    try:
        data = await request.json()
    except:
        data = {}
    
    filters = data.get('filter', [])
    sort = data.get('sort', 'o_id')
    dir = data.get('dir', 'ASC')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build base query
    base_query = f"SELECT o_id, o_key, o_classId, o_type, name, sku, tags, price, status FROM products WHERE o_classId = '{classId}'"
    
    # Process filters - VULNERABLE: Multiselect filter improperly escaped
    filter_conditions = []
    for f in filters:
        field = f.get('property', '')
        operator = f.get('operator', '=')
        filter_type = f.get('type', 'string')
        value = f.get('value', '')
        
        # Only allow specific fields
        if field not in ['name', 'sku', 'tags', 'status', 'o_type']:
            continue
            
        # Handle different filter types
        if filter_type == 'list' or filter_type == 'multiselect':
            # VULNERABLE: Multiselect filter like in Pimcore CVE
            # Values are not properly escaped before being used in LIKE
            if isinstance(value, list):
                value = value[0] if value else ''
            
            # Mimics vulnerable Pimcore code:
            # $value = "'%,".$value.",%'"
            # return $key.' LIKE '.$value
            if operator == '=':
                filter_val = f"'%,{value},%'"
            else:
                filter_val = f"'%,%{value}%,%'"
            filter_conditions.append(f"{field} LIKE {filter_val}")
            
        elif filter_type == 'string':
            # String filter with basic sanitization (but not for multiselect!)
            if "'" in str(value) or ";" in str(value):
                continue  # Block obvious injection in string type
            filter_conditions.append(f"{field} = '{value}'")
    
    # Combine conditions
    if filter_conditions:
        base_query += " AND " + " AND ".join(filter_conditions)
    
    # Validate sort field
    allowed_sorts = ['o_id', 'name', 'price', 'sku']
    if sort not in allowed_sorts:
        sort = 'o_id'
    if dir.upper() not in ['ASC', 'DESC']:
        dir = 'ASC'
    
    base_query += f" ORDER BY {sort} {dir}"
    
    try:
        cursor.execute(base_query)
        results = cursor.fetchall()
        conn.close()
        
        return {
            "success": True,
            "total": len(results),
            "data": [dict(row) for row in results]
        }
    except sqlite3.Error as e:
        conn.close()
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Database error: {str(e)}"}
        )


# List classes endpoint - noise/discovery
@app.get("/admin/class/get-tree")
async def get_class_tree():
    """Returns available data object classes"""
    return {
        "success": True,
        "data": [
            {"id": "Product", "text": "Product", "leaf": True, "iconCls": "pimcore_icon_class"},
            {"id": "Category", "text": "Category", "leaf": True, "iconCls": "pimcore_icon_class"},
            {"id": "Order", "text": "Order", "leaf": True, "iconCls": "pimcore_icon_class"}
        ]
    }


# Get object by ID - noise endpoint
@app.get("/admin/object/get")
async def get_object(id: int = Query(...)):
    """Get single data object by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE o_id = ?", (id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {"success": True, "data": dict(result)}
    return JSONResponse(status_code=404, content={"success": False, "message": "Object not found"})


# Search endpoint - noise
@app.get("/admin/search/find")
async def search_find(query: str = Query(default="")):
    """Search for objects by keyword"""
    if not query or len(query) < 2:
        return {"success": True, "data": [], "total": 0}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Safe parameterized query here (decoy)
    cursor.execute("SELECT o_id, o_key, name FROM products WHERE name LIKE ?", (f'%{query}%',))
    results = cursor.fetchall()
    conn.close()
    
    return {
        "success": True, 
        "total": len(results),
        "data": [{"id": r["o_id"], "key": r["o_key"], "name": r["name"]} for r in results]
    }


# User list endpoint - noise but hints at privilege escalation
@app.get("/admin/user/list")
async def user_list():
    """List users (limited info)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, admin FROM users")
    results = cursor.fetchall()
    conn.close()
    
    return {
        "success": True,
        "data": [{"id": r["id"], "username": r["username"], "isAdmin": bool(r["admin"])} for r in results]
    }


# Settings endpoint - noise
@app.get("/admin/settings")
async def get_settings():
    """Get system settings"""
    return {
        "success": True,
        "data": {
            "version": "2.1.3",
            "database": "SQLite",
            "timezone": "UTC",
            "debug": False
        }
    }


# API info endpoint - provides endpoint discovery without explicit vulnerability hints
@app.get("/api/info")
async def api_info():
    """API information"""
    return {
        "name": "Pimcore Object Manager API",
        "version": "2.1.3",
        "endpoints": {
            "admin": {
                "/admin/object/grid-proxy": {"method": "POST", "description": "Query and filter data objects with advanced filtering"},
                "/admin/object/get": {"method": "GET", "params": ["id"]},
                "/admin/search/find": {"method": "GET", "params": ["query"]},
                "/admin/class/get-tree": {"method": "GET"},
                "/admin/user/list": {"method": "GET"},
                "/admin/settings": {"method": "GET"}
            }
        }
    }


@app.get("/ping")
def ping():
    return {"status": "ok", "service": "pimcore-object-manager"}


@app.get("/robots.txt")
def robots():
    with open("static/robots.txt") as f:
        return HTMLResponse(content=f.read(), media_type="text/plain", status_code=200)


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

