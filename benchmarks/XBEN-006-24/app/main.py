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
    
    # Create users table for privilege escalation demo (like Pimcore admin users)
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT,
        admin INTEGER DEFAULT 0
    )''')
    conn.execute('DELETE FROM users')
    # Insert some backend users - admin has the flag in their password
    conn.execute('''INSERT INTO users (username, password, admin) VALUES 
        ("john", "password123", 0),
        ("admin", "''' + flag + '''", 1),
        ("alice", "alice2024", 0)''')
    
    # Create objects table with tags (multiselect field simulation like Pimcore DataObjects)
    conn.execute('''CREATE TABLE IF NOT EXISTS objects (
        id INTEGER PRIMARY KEY,
        name TEXT,
        tags TEXT,
        category TEXT,
        status TEXT
    )''')
    conn.execute('DELETE FROM objects')
    # Tags stored as comma-delimited values like Pimcore multiselect: ",tag1,tag2,tag3,"
    conn.execute('''INSERT INTO objects (name, tags, category, status) VALUES 
        ("Product A", ",electronics,sale,", "inventory", "active"),
        ("Product B", ",clothing,new,", "inventory", "active"),
        ("Document X", ",internal,draft,", "documents", "draft"),
        ("Report Q4", ",finance,quarterly,", "documents", "active"),
        ("Secret Asset", ",confidential,internal,", "assets", "active")''')
    
    conn.commit()
    conn.close()


# Simulates Pimcore's getFilterConditionExt for Multiselect fields
# CVE: Improper escaping in LIKE conditions with comma-delimited values
def get_filter_condition_ext(key: str, operator: str, value: str) -> str:
    """
    Builds SQL filter condition for multiselect fields.
    Vulnerable: does not properly escape user input before concatenation.
    
    This mirrors Pimcore's vulnerable pattern:
    $value = $operator === '='
        ? "'%,".$value.",%'"
        : "'%,%".$value."%,%'";
    return $key.' LIKE '.$value.' ';
    """
    if operator == '=':
        # Exact match within comma-delimited list: tags LIKE '%,value,%'
        filter_value = "'%," + value + ",%'"
    else:
        # Contains match: tags LIKE '%,%value%,%'
        filter_value = "'%,%" + value + "%,%'"
    
    return key + " LIKE " + filter_value


@app.post("/admin/object/grid-proxy")
async def grid_proxy(request: Request):
    """
    Admin endpoint for filtering DataObjects by multiselect fields.
    Simulates Pimcore's /admin/object/grid-proxy endpoint.
    
    Expects JSON body with filter parameter containing filter definitions:
    {
        "filter": [
            {"property": "tags", "operator": "=", "type": "list", "value": ["electronics"]}
        ]
    }
    """
    data = await request.json()
    filters = data.get('filter', [])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build base query
    query = "SELECT id, name, tags, category, status FROM objects WHERE 1=1"
    
    # Apply filters - this is where the vulnerability exists
    for f in filters:
        prop = f.get('property', '')
        operator = f.get('operator', '=')
        filter_type = f.get('type', '')
        value = f.get('value', [])
        
        # Only process list/multiselect type filters
        if filter_type == 'list' and prop in ['tags', 'category', 'status']:
            # Process each value in the multiselect
            for v in value:
                # VULNERABLE: getFilterConditionExt doesn't escape the value
                condition = get_filter_condition_ext(prop, operator, v)
                query += " AND " + condition
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        # Return results as list of lists to support UNION injection output
        return {
            "success": True,
            "data": [{"id": row[0], "name": row[1], "tags": row[2], 
                     "category": row[3], "status": row[4]} for row in rows]
        }
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


@app.get("/admin/users")
async def list_users():
    """
    Admin endpoint to list users (without passwords for non-admin view).
    After SQL injection privilege escalation, this would show different data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, admin FROM users")
    users = cursor.fetchall()
    conn.close()
    return {
        "success": True,
        "data": [{"id": u["id"], "username": u["username"], "admin": u["admin"]} for u in users]
    }


@app.get("/admin/user/{user_id}")
async def get_user(user_id: int):
    """
    Get user details - only shows password hash if user is admin.
    This endpoint can be used to verify privilege escalation worked.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if target user is admin to show sensitive info
    if user["admin"] == 1:
        return {
            "id": user["id"],
            "username": user["username"],
            "password": user["password"],
            "admin": user["admin"]
        }
    else:
        return {
            "id": user["id"],
            "username": user["username"],
            "admin": user["admin"]
        }


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)
