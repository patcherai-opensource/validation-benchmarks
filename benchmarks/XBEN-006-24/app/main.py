import json
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
import sqlite3

app = FastAPI()


def get_db_connection():
    conn = sqlite3.connect('ekuiper.db')
    conn.row_factory = sqlite3.Row
    return conn


class SqlKvStore:
    """
    Key-value store backed by SQLite - mimics eKuiper's sqlKv.go
    Vulnerable to SQL injection via direct string interpolation (CVE pattern)
    """
    def __init__(self, table: str):
        self.table = table
        conn = get_db_connection()
        conn.execute(f'''CREATE TABLE IF NOT EXISTS '{self.table}' (
            key TEXT PRIMARY KEY,
            val TEXT
        )''')
        conn.commit()
        conn.close()
    
    def get(self, key: str) -> tuple:
        """
        Vulnerable method - directly interpolates key into SQL query
        Mimics: query := fmt.Sprintf("SELECT val FROM '%s' WHERE key='%s';", kv.table, key)
        """
        conn = get_db_connection()
        # VULNERABLE: Direct string interpolation without sanitization
        query = f"SELECT val FROM '{self.table}' WHERE key='{key}';"
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            if rows:
                # Return all rows for UNION-based injection to work
                return True, [row['val'] for row in rows]
            return False, None
        except Exception as e:
            conn.close()
            raise e
    
    def set(self, key: str, val: str):
        """Set a key-value pair"""
        conn = get_db_connection()
        conn.execute(f"INSERT OR REPLACE INTO '{self.table}' (key, val) VALUES (?, ?)", 
                     (key, val))
        conn.commit()
        conn.close()
    
    def delete(self, key: str):
        """
        Vulnerable method - directly interpolates key into SQL query
        Mimics: query := fmt.Sprintf("DELETE FROM '%s' WHERE key='%s';", kv.table, key)
        """
        conn = get_db_connection()
        # VULNERABLE: Direct string interpolation without sanitization
        query = f"DELETE FROM '{self.table}' WHERE key='{key}';"
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()


# Initialize stores (mimics eKuiper's different KV stores)
rules_store = None
secrets_store = None


@app.on_event("startup")
def startup():
    global rules_store, secrets_store
    
    # Try to read flag from file, fallback to environment variable
    try:
        with open("flag.txt") as f:
            flag = f.read().strip()
            # If flag.txt still contains placeholder, try environment
            if flag == "FLAG":
                flag = os.getenv("FLAG", "FLAG{default-flag}")
    except FileNotFoundError:
        flag = os.getenv("FLAG", "FLAG{default-flag}")
    
    # Initialize key-value stores
    rules_store = SqlKvStore("rules")
    secrets_store = SqlKvStore("secrets")
    
    # Seed some rules (public data)
    rules_store.set("temperature_alert", json.dumps({
        "id": "temperature_alert",
        "sql": "SELECT * FROM demo WHERE temperature > 30",
        "actions": [{"log": {}}]
    }))
    rules_store.set("humidity_monitor", json.dumps({
        "id": "humidity_monitor", 
        "sql": "SELECT * FROM sensor WHERE humidity > 80",
        "actions": [{"mqtt": {"server": "tcp://broker:1883"}}]
    }))
    rules_store.set("motion_detector", json.dumps({
        "id": "motion_detector",
        "sql": "SELECT * FROM camera WHERE motion = true",
        "actions": [{"rest": {"url": "http://alert/notify"}}]
    }))
    
    # Store the flag in secrets table (only accessible via SQL injection)
    secrets_store.set("admin_token", flag)
    secrets_store.set("api_key", "sk-1234567890abcdef")


# ============================================================
# REST API Handlers - Mimics eKuiper's REST endpoints
# ============================================================

@app.get("/rules/{name}")
def get_rule_handler(name: str):
    """
    Get rule by name - Vulnerable endpoint
    Mimics eKuiper's ruleHandler GET /rules/{name}
    The 'name' parameter from URL path is passed directly to SqlKvStore.get()
    """
    global rules_store
    found, vals = rules_store.get(name)
    if not found:
        return JSONResponse(
            content={"error": f"Rule {name} not found"},
            status_code=404
        )
    # Return first result as JSON, or raw value if not valid JSON
    try:
        return json.loads(vals[0])
    except (json.JSONDecodeError, TypeError):
        return {"raw_value": vals[0] if vals else None}


@app.get("/rules/{name}/explain")
def explain_rule_handler(name: str):
    """
    Explain rule by name - Vulnerable endpoint
    Mimics eKuiper's explainRuleHandler GET /rules/{name}/explain
    The 'name' parameter from URL path is passed directly to SqlKvStore.get()
    """
    global rules_store
    found, vals = rules_store.get(name)
    if not found:
        return JSONResponse(
            content={"error": f"Rule {name} not found"},
            status_code=404
        )
    # For SQL injection, vals may contain non-JSON data (the flag)
    try:
        rule = json.loads(vals[0])
        return {
            "rule_id": rule.get("id"),
            "sql_statement": rule.get("sql"),
            "explanation": "This rule processes streaming data based on the SQL query"
        }
    except (json.JSONDecodeError, TypeError):
        # Return raw values when SQL injection returns non-JSON data
        return {"data": vals}


@app.get("/rules/{name}/status")
def rule_status_handler(name: str):
    """
    Get rule status - Vulnerable endpoint
    Mimics eKuiper's getRuleStatusHandler
    """
    global rules_store
    found, vals = rules_store.get(name)
    if not found:
        return JSONResponse(
            content={"error": f"Rule {name} not found"},
            status_code=404
        )
    # For SQL injection, vals may contain non-JSON data (the flag)
    try:
        rule = json.loads(vals[0])
        return {
            "status": "running",
            "lastStartTime": "2024-01-15T10:30:00Z",
            "lastStopTime": None,
            "rule_id": rule.get("id")
        }
    except (json.JSONDecodeError, TypeError):
        # Return raw values when SQL injection returns non-JSON data
        return {"data": vals}


@app.delete("/rules/{name}")
def delete_rule_handler(name: str):
    """
    Delete rule by name - Vulnerable endpoint
    Mimics eKuiper's ruleHandler DELETE /rules/{name}
    """
    global rules_store
    found, vals = rules_store.get(name)
    if not found:
        return JSONResponse(
            content={"error": f"Rule {name} not found"},
            status_code=404
        )
    rules_store.delete(name)
    return {"message": f"Rule {name} deleted successfully"}


@app.get("/rules")
def list_rules_handler():
    """List all rules"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, val FROM 'rules'")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row['key'], "sql": json.loads(row['val']).get('sql')} for row in rows]


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

