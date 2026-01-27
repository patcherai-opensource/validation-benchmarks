import json
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
import sqlite3

app = FastAPI()


def get_db_connection():
    conn = sqlite3.connect('pimcore.db')
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
    
    # Create users table with admin flag
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        email TEXT,
        role TEXT,
        notes TEXT
    )''')
    conn.execute('DELETE FROM users')
    conn.execute(
        'INSERT INTO users (username, email, role, notes) VALUES '
        '("editor", "editor@example.com", "editor", "Content editor account"), '
        '("viewer", "viewer@example.com", "viewer", "Read-only account"), '
        f'("superadmin", "admin@internal.local", "admin", "{flag}"), '
        '("moderator", "mod@example.com", "moderator", "Moderator account")')
    
    # Create data_objects table (content management objects)
    conn.execute('''CREATE TABLE IF NOT EXISTS data_objects (
        id INTEGER PRIMARY KEY,
        o_key TEXT,
        o_className TEXT,
        o_path TEXT,
        tags TEXT,
        published INTEGER
    )''')
    conn.execute('DELETE FROM data_objects')
    conn.execute(
        'INSERT INTO data_objects (o_key, o_className, o_path, tags, published) VALUES '
        '("homepage", "Page", "/", "featured,public", 1), '
        '("about-us", "Page", "/company/", "company,public", 1), '
        '("contact", "Page", "/company/", "contact,public", 1), '
        '("product-1", "Product", "/shop/", "electronics,sale", 1), '
        '("product-2", "Product", "/shop/", "electronics,new", 1), '
        '("draft-page", "Page", "/drafts/", "internal,draft", 0)')
    
    conn.commit()
    conn.close()


def build_filter_condition(filter_data):
    """Build SQL filter condition from grid filter data - Multiselect filter handling"""
    conditions = []
    
    for f in filter_data:
        prop = f.get('property', '')
        operator = f.get('operator', '=')
        value = f.get('value', '')
        filter_type = f.get('type', 'string')
        
        # Basic validation
        if not prop or not value:
            continue
            
        # Handle multiselect/list type filters (vulnerable path - mimics Pimcore CVE)
        if filter_type == 'list':
            # Multiselect stores values as comma-separated: ",value1,value2,"
            if isinstance(value, list):
                value = value[0] if value else ''
            
            # Vulnerable: directly concatenates user input into LIKE pattern
            # Mimics: $value = "'%,".$value.",%'"  from Pimcore
            if operator == '=':
                like_pattern = f"%,{value},%"
            else:
                like_pattern = f"%,%{value}%,%"
            
            conditions.append(f"{prop} LIKE '{like_pattern}'")
        else:
            # String filter - also vulnerable but different path
            conditions.append(f"{prop} = '{value}'")
    
    return " AND ".join(conditions) if conditions else "1=1"


@app.post("/admin/object/grid-proxy")
async def grid_proxy(request: Request):
    """
    Grid proxy endpoint for data object listing with filters.
    Accepts filter parameter as JSON array similar to Pimcore's grid filtering.
    """
    data = await request.json()
    
    class_name = data.get('className', 'DataObject')
    filter_data = data.get('filter', [])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if filter_data:
            filter_condition = build_filter_condition(filter_data)
            query = f"SELECT * FROM data_objects WHERE {filter_condition}"
        else:
            query = "SELECT * FROM data_objects WHERE published = 1"
        
        print(f"[DEBUG] Executing query: {query}")
        cursor.execute(query)
        objects = cursor.fetchall()
        
        result = {
            "success": True,
            "total": len(objects),
            "data": [
                {
                    "id": obj["id"],
                    "key": obj["o_key"],
                    "className": obj["o_className"],
                    "path": obj["o_path"],
                    "tags": obj["tags"],
                    "published": bool(obj["published"])
                }
                for obj in objects
            ]
        }
    except sqlite3.Error as e:
        result = {
            "success": False,
            "message": f"Database error: {str(e)}",
            "total": 0,
            "data": []
        }
    finally:
        conn.close()
    
    return result


@app.get("/admin/user/list")
async def user_list():
    """
    List users - but only non-admin users are shown publicly.
    Admin user notes contain sensitive information.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Only show non-admin users
    cursor.execute("SELECT id, username, email, role FROM users WHERE role != 'admin'")
    users = cursor.fetchall()
    conn.close()
    
    return {
        "success": True,
        "total": len(users),
        "data": [
            {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"]
            }
            for user in users
        ]
    }


@app.get("/ping")
def ping():
    return {"status": "ok", "service": "pimcore-cms"}


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

