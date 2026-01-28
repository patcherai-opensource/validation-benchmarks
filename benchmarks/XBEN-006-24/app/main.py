import json
import os
import hashlib
import secrets
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Response, Cookie, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import sqlite3

app = FastAPI()

# Session management
active_sessions = {}

def get_db_connection():
    conn = sqlite3.connect('netmon.db')
    conn.row_factory = sqlite3.Row
    return conn


def verify_session(session_id: str) -> bool:
    """Check if session is valid"""
    return session_id in active_sessions


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
    
    # Users table for authentication
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT DEFAULT 'viewer'
    )''')
    
    # Network devices table
    conn.execute('''CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY,
        hostname TEXT,
        ip_address TEXT,
        mac_address TEXT,
        device_type TEXT,
        location TEXT,
        status TEXT DEFAULT 'active',
        last_seen TEXT
    )''')
    
    # Ports/interfaces table
    conn.execute('''CREATE TABLE IF NOT EXISTS interfaces (
        id INTEGER PRIMARY KEY,
        device_id INTEGER,
        if_name TEXT,
        if_phys_address TEXT,
        if_speed INTEGER,
        if_status TEXT,
        description TEXT,
        FOREIGN KEY (device_id) REFERENCES devices(id)
    )''')
    
    # System config table (stores sensitive data)
    conn.execute('''CREATE TABLE IF NOT EXISTS system_config (
        id INTEGER PRIMARY KEY,
        config_key TEXT UNIQUE,
        config_value TEXT,
        is_sensitive INTEGER DEFAULT 0
    )''')
    
    # Clear tables for fresh start
    conn.execute('DELETE FROM users')
    conn.execute('DELETE FROM devices')
    conn.execute('DELETE FROM interfaces')
    conn.execute('DELETE FROM system_config')
    
    # Insert default users
    admin_hash = hashlib.sha256("netmon_admin_2024!".encode()).hexdigest()
    viewer_hash = hashlib.sha256("viewer123".encode()).hexdigest()
    conn.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                 ('admin', admin_hash, 'admin'))
    conn.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                 ('monitor', viewer_hash, 'viewer'))
    
    # Insert network devices
    devices_data = [
        ('core-switch-01', '192.168.1.1', 'AA:BB:CC:DD:EE:01', 'switch', 'DataCenter-A', 'active'),
        ('core-switch-02', '192.168.1.2', 'AA:BB:CC:DD:EE:02', 'switch', 'DataCenter-A', 'active'),
        ('edge-router-01', '10.0.0.1', 'AA:BB:CC:DD:EE:03', 'router', 'DataCenter-B', 'active'),
        ('wifi-ap-floor1', '192.168.10.100', 'AA:BB:CC:DD:EE:04', 'access_point', 'Office-Floor1', 'active'),
        ('wifi-ap-floor2', '192.168.10.101', 'AA:BB:CC:DD:EE:05', 'access_point', 'Office-Floor2', 'warning'),
        ('firewall-main', '10.0.0.254', 'AA:BB:CC:DD:EE:06', 'firewall', 'DataCenter-A', 'active'),
        ('nas-backup-01', '192.168.5.10', 'AA:BB:CC:DD:EE:07', 'storage', 'DataCenter-B', 'active'),
        ('server-web-01', '192.168.2.10', 'AA:BB:CC:DD:EE:08', 'server', 'DataCenter-A', 'active'),
        ('server-db-01', '192.168.2.20', 'AA:BB:CC:DD:EE:09', 'server', 'DataCenter-A', 'active'),
        ('printer-office', '192.168.10.50', 'AA:BB:CC:DD:EE:0A', 'printer', 'Office-Floor1', 'offline'),
    ]
    
    for hostname, ip, mac, dtype, location, status in devices_data:
        conn.execute(
            'INSERT INTO devices (hostname, ip_address, mac_address, device_type, location, status, last_seen) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (hostname, ip, mac, dtype, location, status, datetime.now().isoformat())
        )
    
    # Insert interfaces with MAC addresses
    interfaces_data = [
        (1, 'eth0', 'AA:BB:CC:11:22:01', 1000, 'up', 'Uplink to core'),
        (1, 'eth1', 'AA:BB:CC:11:22:02', 1000, 'up', 'Server VLAN'),
        (1, 'eth2', 'AA:BB:CC:11:22:03', 100, 'down', 'Unused port'),
        (2, 'ge-0/0/0', 'AA:BB:CC:22:33:01', 10000, 'up', 'Primary uplink'),
        (2, 'ge-0/0/1', 'AA:BB:CC:22:33:02', 10000, 'up', 'Secondary uplink'),
        (3, 'wan0', 'AA:BB:CC:33:44:01', 1000, 'up', 'Internet connection'),
        (3, 'lan0', 'AA:BB:CC:33:44:02', 1000, 'up', 'Internal network'),
        (4, 'wlan0', 'AA:BB:CC:44:55:01', 0, 'up', '2.4GHz radio'),
        (4, 'wlan1', 'AA:BB:CC:44:55:02', 0, 'up', '5GHz radio'),
        (6, 'mgmt0', 'AA:BB:CC:66:77:01', 1000, 'up', 'Management interface'),
    ]
    
    for dev_id, if_name, mac, speed, status, desc in interfaces_data:
        conn.execute(
            'INSERT INTO interfaces (device_id, if_name, if_phys_address, if_speed, if_status, description) VALUES (?, ?, ?, ?, ?, ?)',
            (dev_id, if_name, mac, speed, status, desc)
        )
    
    # Insert system config - flag stored as sensitive API key
    conn.execute('INSERT INTO system_config (config_key, config_value, is_sensitive) VALUES (?, ?, ?)',
                 ('site_name', 'NetMon Enterprise', 0))
    conn.execute('INSERT INTO system_config (config_key, config_value, is_sensitive) VALUES (?, ?, ?)',
                 ('alert_email', 'alerts@company.local', 0))
    conn.execute('INSERT INTO system_config (config_key, config_value, is_sensitive) VALUES (?, ?, ?)',
                 ('snmp_community', 'public', 0))
    conn.execute('INSERT INTO system_config (config_key, config_value, is_sensitive) VALUES (?, ?, ?)',
                 ('backup_api_key', flag, 1))
    conn.execute('INSERT INTO system_config (config_key, config_value, is_sensitive) VALUES (?, ?, ?)',
                 ('retention_days', '90', 0))
    
    conn.commit()
    conn.close()


@app.get("/ping")
def ping():
    return {"status": "ok", "service": "netmon"}


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/login", response_class=HTMLResponse)
def login_page():
    with open("static/login.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.post("/api/auth/login")
async def login(request: Request):
    data = await request.json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    if not username or not password:
        return JSONResponse({"error": "Missing credentials"}, status_code=400)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute('SELECT id, username, role FROM users WHERE username = ? AND password_hash = ?',
                   (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session_id = secrets.token_hex(32)
        active_sessions[session_id] = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
        response = JSONResponse({"success": True, "message": "Login successful", "role": user['role']})
        response.set_cookie(key="session", value=session_id, httponly=True)
        return response
    
    return JSONResponse({"error": "Invalid credentials"}, status_code=401)


@app.post("/api/auth/logout")
async def logout(session: str = Cookie(default=None)):
    if session and session in active_sessions:
        del active_sessions[session]
    response = JSONResponse({"success": True})
    response.delete_cookie("session")
    return response


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(session: str = Cookie(default=None)):
    if not session or not verify_session(session):
        return RedirectResponse(url="/login", status_code=302)
    with open("static/dashboard.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/api/devices")
async def list_devices(session: str = Cookie(default=None)):
    if not session or not verify_session(session):
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, hostname, ip_address, mac_address, device_type, location, status, last_seen FROM devices')
    devices = cursor.fetchall()
    conn.close()
    
    return [dict(d) for d in devices]


@app.get("/api/devices/{device_id}")
async def get_device(device_id: int, session: str = Cookie(default=None)):
    if not session or not verify_session(session):
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
    device = cursor.fetchone()
    
    if not device:
        conn.close()
        return JSONResponse({"error": "Device not found"}, status_code=404)
    
    cursor.execute('SELECT * FROM interfaces WHERE device_id = ?', (device_id,))
    interfaces = cursor.fetchall()
    conn.close()
    
    return {
        "device": dict(device),
        "interfaces": [dict(i) for i in interfaces]
    }


@app.get("/api/stats")
async def get_stats(session: str = Cookie(default=None)):
    if not session or not verify_session(session):
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM devices')
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as active FROM devices WHERE status = 'active'")
    active = cursor.fetchone()['active']
    
    cursor.execute("SELECT COUNT(*) as warning FROM devices WHERE status = 'warning'")
    warning = cursor.fetchone()['warning']
    
    cursor.execute("SELECT COUNT(*) as offline FROM devices WHERE status = 'offline'")
    offline = cursor.fetchone()['offline']
    
    conn.close()
    
    return {
        "total_devices": total,
        "active": active,
        "warning": warning,
        "offline": offline
    }


@app.get("/search/mac", response_class=HTMLResponse)
def mac_search_page(session: str = Cookie(default=None)):
    if not session or not verify_session(session):
        return RedirectResponse(url="/login", status_code=302)
    with open("static/mac_search.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.post("/api/search/address")
async def address_search(request: Request, session: str = Cookie(default=None)):
    """
    Search for interfaces by MAC address.
    Mimics LibreNMS address-search functionality.
    """
    if not session or not verify_session(session):
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    data = await request.json()
    address = data.get('address', '')
    
    if not address:
        return JSONResponse({"error": "Address parameter required"}, status_code=400)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sanitize input - remove common MAC address separators
    # This mimics the vulnerable pattern from LibreNMS CVE-2023-5591
    # str_replace([':', ' ', '-', '.', '0x'], '', $vars['address'])
    sanitized = address
    for char in [':', ' ', '-', '.', '0x']:
        sanitized = sanitized.replace(char, '')
    
    # Vulnerable query - user input directly interpolated after sanitization
    # This is the same pattern as the CVE where sanitization isn't sufficient
    query = f"SELECT I.id, I.device_id, I.if_name, I.if_phys_address, I.if_speed, I.if_status, I.description, D.hostname, D.ip_address FROM interfaces I, devices D WHERE I.device_id = D.id AND I.if_phys_address LIKE '%{sanitized}%'"
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return {
            "query_executed": True,
            "results": [dict(r) for r in results]
        }
    except Exception as e:
        conn.close()
        # Return SQL error for debugging - realistic behavior that aids exploitation
        return JSONResponse({
            "error": "Database query failed",
            "detail": str(e)
        }, status_code=500)


@app.get("/api/config")
async def get_config(session: str = Cookie(default=None)):
    """Get non-sensitive configuration values"""
    if not session or not verify_session(session):
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Only return non-sensitive config
    cursor.execute('SELECT config_key, config_value FROM system_config WHERE is_sensitive = 0')
    config = cursor.fetchall()
    conn.close()
    
    return {item['config_key']: item['config_value'] for item in config}


@app.get("/api/alerts")
async def get_alerts(session: str = Cookie(default=None)):
    """Get recent alerts - placeholder endpoint"""
    if not session or not verify_session(session):
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    return {
        "alerts": [
            {"id": 1, "severity": "warning", "message": "High CPU usage on core-switch-01", "timestamp": "2024-01-15T10:30:00"},
            {"id": 2, "severity": "critical", "message": "printer-office is offline", "timestamp": "2024-01-15T09:15:00"},
            {"id": 3, "severity": "info", "message": "Backup completed successfully", "timestamp": "2024-01-15T06:00:00"},
        ]
    }


@app.get("/settings", response_class=HTMLResponse)
def settings_page(session: str = Cookie(default=None)):
    if not session or not verify_session(session):
        return RedirectResponse(url="/login", status_code=302)
    with open("static/settings.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

