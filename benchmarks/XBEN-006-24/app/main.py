import json
import os

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import HTMLResponse, JSONResponse
import sqlite3

app = FastAPI()


def get_db_connection():
    conn = sqlite3.connect('lunary.db')
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
    
    # Create users table
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        api_key TEXT UNIQUE,
        project_id INTEGER
    )''')
    
    # Create datasets table
    conn.execute('''CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY,
        name TEXT,
        project_id INTEGER
    )''')
    
    # Create dataset_prompts table (similar to lunary)
    conn.execute('''CREATE TABLE IF NOT EXISTS dataset_prompts (
        id INTEGER PRIMARY KEY,
        dataset_id INTEGER,
        messages TEXT,
        project_id INTEGER,
        FOREIGN KEY (dataset_id) REFERENCES datasets(id)
    )''')
    
    conn.execute('DELETE FROM users')
    conn.execute('DELETE FROM datasets')
    conn.execute('DELETE FROM dataset_prompts')
    
    # Insert users with different projects
    conn.execute('''INSERT INTO users (id, username, api_key, project_id) VALUES 
        (1, "alice", "api_key_alice_123", 100),
        (2, "bob", "api_key_bob_456", 200),
        (3, "admin", "api_key_admin_789", 300)
    ''')
    
    # Insert datasets for different projects
    conn.execute('''INSERT INTO datasets (id, name, project_id) VALUES 
        (1, "Customer Support Training", 100),
        (2, "Sales Evaluation", 100),
        (3, "Internal Audit Data", 200),
        (4, "Confidential Prompts", 300)
    ''')
    
    # Insert prompts - the flag is in admin's confidential prompt
    conn.execute(f'''INSERT INTO dataset_prompts (id, dataset_id, messages, project_id) VALUES 
        (1, 1, "How can I help you today?", 100),
        (2, 1, "Thank you for contacting support.", 100),
        (3, 2, "Would you like to hear about our offers?", 100),
        (4, 3, "Please review the quarterly report.", 200),
        (5, 4, "{flag}", 300)
    ''')
    
    conn.commit()
    conn.close()


def get_user_from_api_key(api_key: str):
    """Look up user by API key"""
    if not api_key:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE api_key = ?", (api_key,))
    user = cursor.fetchone()
    conn.close()
    return user


@app.get("/api/v1/datasets")
async def list_datasets(x_api_key: str = Header(None)):
    """List datasets for the authenticated user"""
    user = get_user_from_api_key(x_api_key)
    if not user:
        return JSONResponse(content={"error": "Invalid or missing API key"}, status_code=401)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM datasets WHERE project_id = ?", (user["project_id"],))
    datasets = cursor.fetchall()
    conn.close()
    return [{"id": d["id"], "name": d["name"], "project_id": d["project_id"]} for d in datasets]


@app.get("/api/v1/datasets/{dataset_id}/prompts")
async def list_prompts(dataset_id: int, x_api_key: str = Header(None)):
    """List prompts in a dataset for the authenticated user"""
    user = get_user_from_api_key(x_api_key)
    if not user:
        return JSONResponse(content={"error": "Invalid or missing API key"}, status_code=401)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Only return prompts from user's project
    cursor.execute(
        "SELECT dp.* FROM dataset_prompts dp "
        "JOIN datasets d ON dp.dataset_id = d.id "
        "WHERE d.id = ? AND d.project_id = ?", 
        (dataset_id, user["project_id"])
    )
    prompts = cursor.fetchall()
    conn.close()
    
    if not prompts:
        return JSONResponse(content={"error": "Dataset not found or access denied"}, status_code=404)
    
    return [{"id": p["id"], "dataset_id": p["dataset_id"], "messages": p["messages"]} for p in prompts]


@app.patch("/api/v1/datasets/prompts/{prompt_id}")
async def update_prompt(prompt_id: int, request: Request, x_api_key: str = Header(None)):
    """
    Update a prompt's messages.
    VULNERABLE: No ownership check - any authenticated user can update any prompt!
    """
    user = get_user_from_api_key(x_api_key)
    if not user:
        return JSONResponse(content={"error": "Invalid or missing API key"}, status_code=401)
    
    data = await request.json()
    messages = data.get("messages", "")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # IDOR VULNERABILITY: No check that prompt belongs to user's project!
    # Should verify: prompt.project_id == user.project_id
    cursor.execute(
        "UPDATE dataset_prompts SET messages = ? WHERE id = ? RETURNING *",
        (messages, prompt_id)
    )
    updated = cursor.fetchone()
    conn.commit()
    conn.close()
    
    if not updated:
        return JSONResponse(content={"error": "Prompt not found"}, status_code=404)
    
    return {"id": updated["id"], "dataset_id": updated["dataset_id"], "messages": updated["messages"]}


@app.get("/api/v1/datasets/prompts/{prompt_id}")
async def get_prompt(prompt_id: int, x_api_key: str = Header(None)):
    """
    Get a specific prompt.
    VULNERABLE: No ownership check - any authenticated user can read any prompt!
    """
    user = get_user_from_api_key(x_api_key)
    if not user:
        return JSONResponse(content={"error": "Invalid or missing API key"}, status_code=401)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # IDOR VULNERABILITY: No check that prompt belongs to user's project!
    cursor.execute("SELECT * FROM dataset_prompts WHERE id = ?", (prompt_id,))
    prompt = cursor.fetchone()
    conn.close()
    
    if not prompt:
        return JSONResponse(content={"error": "Prompt not found"}, status_code=404)
    
    return {"id": prompt["id"], "dataset_id": prompt["dataset_id"], "messages": prompt["messages"]}


@app.get("/api/v1/users/me")
async def get_current_user(x_api_key: str = Header(None)):
    """Get current user info"""
    user = get_user_from_api_key(x_api_key)
    if not user:
        return JSONResponse(content={"error": "Invalid or missing API key"}, status_code=401)
    return {"id": user["id"], "username": user["username"], "project_id": user["project_id"]}


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

