import json
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
import sqlite3

app = FastAPI(title="eKuiper Stream Processing Manager", version="1.14.1")


def get_db_connection():
    conn = sqlite3.connect('kuiper.db')
    conn.row_factory = sqlite3.Row
    return conn


class SqlKvStore:
    """Key-value store backed by SQLite - simulating eKuiper's sqlKv.go"""
    
    def __init__(self, table_name: str):
        self.table = table_name
    
    def get(self, key: str):
        """
        Get a value by key from the store.
        WARNING: This method directly interpolates user input into SQL (vulnerable)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        # Vulnerable: direct string interpolation like eKuiper's sqlKv.go
        query = f"SELECT val FROM '{self.table}' WHERE key='{key}';"
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            if rows:
                # Return first result (or concatenate if multiple from UNION)
                return rows[0]['val']
            return None
        except sqlite3.Error as e:
            conn.close()
            # Expose SQL error details for debugging (vulnerable to information disclosure)
            raise Exception(f"database query failed: {str(e)} [query: {query}]")
    
    def get_all(self):
        """Get all key-value pairs from the store"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT key, val FROM '{self.table}'")
        rows = cursor.fetchall()
        conn.close()
        return {row['key']: row['val'] for row in rows}


# Global stores for rules and configs
rule_store = SqlKvStore("rules")
config_store = SqlKvStore("configs")


@app.on_event("startup")
def startup():
    # Try to read flag from file, fallback to environment variable
    try:
        with open("flag.txt") as f:
            flag = f.read().strip()
            if flag == "FLAG":
                flag = os.getenv("FLAG", "FLAG{default-flag}")
    except FileNotFoundError:
        flag = os.getenv("FLAG", "FLAG{default-flag}")

    conn = get_db_connection()
    
    # Create rules table (key-value store for stream processing rules)
    conn.execute('''CREATE TABLE IF NOT EXISTS rules (
        key TEXT PRIMARY KEY,
        val TEXT
    )''')
    
    # Create configs table (key-value store for system configurations)
    conn.execute('''CREATE TABLE IF NOT EXISTS configs (
        key TEXT PRIMARY KEY,
        val TEXT
    )''')
    
    # Create internal credentials table (stores admin secrets)
    conn.execute('''CREATE TABLE IF NOT EXISTS admin_credentials (
        id INTEGER PRIMARY KEY,
        username TEXT,
        secret TEXT
    )''')
    
    conn.execute('DELETE FROM rules')
    conn.execute('DELETE FROM configs')
    conn.execute('DELETE FROM admin_credentials')
    
    # Insert sample stream processing rules
    rules_data = [
        ('mqtt_ingest', '{"id":"mqtt_ingest","sql":"SELECT * FROM mqtt_stream","actions":[{"log":{}}],"options":{"sendMetaToSink":true}}'),
        ('kafka_transform', '{"id":"kafka_transform","sql":"SELECT temperature, humidity FROM sensor_data WHERE temperature > 25","actions":[{"kafka":{"brokers":["localhost:9092"],"topic":"alerts"}}]}'),
        ('http_push', '{"id":"http_push","sql":"SELECT deviceId, status FROM device_stream","actions":[{"rest":{"url":"http://backend/api/status"}}]}'),
        ('aggregate_stats', '{"id":"aggregate_stats","sql":"SELECT AVG(value) as avg_val FROM metrics GROUP BY TUMBLINGWINDOW(ss, 60)","actions":[{"influxdb":{"addr":"http://influxdb:8086"}}]}'),
    ]
    
    for key, val in rules_data:
        conn.execute('INSERT INTO rules (key, val) VALUES (?, ?)', (key, val))
    
    # Insert system configurations
    configs_data = [
        ('mqtt', '{"server":"tcp://broker.hivemq.com:1883","format":"json"}'),
        ('kafka', '{"brokers":["kafka:9092"],"groupId":"ekuiper-group"}'),
        ('log_level', '"info"'),
    ]
    
    for key, val in configs_data:
        conn.execute('INSERT INTO configs (key, val) VALUES (?, ?)', (key, val))
    
    # Insert admin credentials with the flag
    conn.execute(
        'INSERT INTO admin_credentials (username, secret) VALUES (?, ?)',
        ('admin', flag)
    )
    
    conn.commit()
    conn.close()


@app.get("/ping")
def ping():
    return {"status": "ok", "version": "1.14.1"}


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


# Rules API endpoints - simulating eKuiper's REST API
@app.get("/rules")
def list_rules():
    """List all stream processing rules"""
    try:
        rules = rule_store.get_all()
        return [{"id": k, "status": "running"} for k in rules.keys()]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/rules/{name}")
def get_rule(name: str):
    """Get a specific rule by name"""
    try:
        rule_data = rule_store.get(name)
        if rule_data is None:
            return JSONResponse(status_code=404, content={"error": f"rule {name} not found"})
        return json.loads(rule_data)
    except json.JSONDecodeError as e:
        # Return the raw data if it's not valid JSON (allows seeing raw query results)
        return JSONResponse(status_code=500, content={"error": f"invalid JSON in rule data", "raw_data": rule_data})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/rules/{name}/explain")
def explain_rule(name: str):
    """
    Explain the execution plan for a rule.
    This endpoint is vulnerable to SQL injection via the {name} path parameter.
    """
    try:
        rule_data = rule_store.get(name)
        if rule_data is None:
            return JSONResponse(status_code=404, content={"error": f"rule {name} not found"})
        
        rule = json.loads(rule_data)
        # Return execution plan explanation
        return {
            "rule_id": rule.get("id"),
            "sql": rule.get("sql"),
            "plan": {
                "type": "stream_processor",
                "source": "memory_source",
                "sink": list(rule.get("actions", [{}])[0].keys())[0] if rule.get("actions") else "unknown"
            }
        }
    except json.JSONDecodeError:
        # Return the raw data if it's not valid JSON (allows seeing raw query results)
        return JSONResponse(status_code=500, content={"error": "invalid rule format", "raw_data": rule_data})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.delete("/rules/{name}")
def delete_rule(name: str):
    """Delete a rule - also vulnerable to SQL injection"""
    try:
        existing = rule_store.get(name)
        if existing is None:
            return JSONResponse(status_code=404, content={"error": f"rule {name} not found"})
        # For demo purposes, we don't actually delete
        return {"message": f"rule {name} deleted"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Configs/Sources API endpoints
@app.get("/configs")
def list_configs():
    """List all configurations"""
    try:
        configs = config_store.get_all()
        return list(configs.keys())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/configs/{name}")
def get_config(name: str):
    """Get a specific configuration by name - vulnerable to SQL injection"""
    try:
        config_data = config_store.get(name)
        if config_data is None:
            return JSONResponse(status_code=404, content={"error": f"config {name} not found"})
        return json.loads(config_data)
    except json.JSONDecodeError as e:
        # Return the raw data if it's not valid JSON (allows seeing raw query results)
        return JSONResponse(status_code=500, content={"error": f"invalid JSON in config data", "raw_data": config_data})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

