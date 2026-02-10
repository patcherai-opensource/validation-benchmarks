import json
import os
import base64
import secrets

from fastapi import FastAPI, HTTPException, Request, Depends, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import sqlite3

app = FastAPI()
security = HTTPBasic()

# Simple session store (in production would use proper session management)
sessions = {}

# Demo users for authentication (CVE requires low-privilege authenticated access)
USERS = {
    "admin": "admin123",
    "user": "user123",
    "operator": "netmon2023"
}


def get_db_connection():
    conn = sqlite3.connect('librenms.db')
    conn.row_factory = sqlite3.Row
    return conn


def check_auth(session_id: str = Cookie(default=None)):
    """Check if user is authenticated via session cookie"""
    if session_id and session_id in sessions:
        return sessions[session_id]
    return None


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
    
    # Create devices table (network devices)
    conn.execute('''CREATE TABLE IF NOT EXISTS devices (
        device_id INTEGER PRIMARY KEY,
        hostname TEXT,
        sysName TEXT,
        hardware TEXT,
        os TEXT
    )''')
    
    # Create ports/interfaces table with MAC addresses
    conn.execute('''CREATE TABLE IF NOT EXISTS ports (
        port_id INTEGER PRIMARY KEY,
        device_id INTEGER,
        ifDescr TEXT,
        ifPhysAddress TEXT,
        ifOperStatus TEXT,
        FOREIGN KEY (device_id) REFERENCES devices(device_id)
    )''')
    
    # Create a secrets table where the flag is stored
    conn.execute('''CREATE TABLE IF NOT EXISTS secrets (
        id INTEGER PRIMARY KEY,
        name TEXT,
        value TEXT
    )''')
    
    # Clear tables for fresh start
    conn.execute('DELETE FROM devices')
    conn.execute('DELETE FROM ports')
    conn.execute('DELETE FROM secrets')
    
    # Insert sample network devices
    conn.execute('''INSERT INTO devices (device_id, hostname, sysName, hardware, os) VALUES 
        (1, "core-switch-01", "core-switch-01.lan", "Cisco Catalyst 9300", "ios-xe"),
        (2, "access-switch-02", "access-switch-02.lan", "Cisco Catalyst 2960", "ios"),
        (3, "router-edge-01", "router-edge-01.lan", "Cisco ISR 4451", "ios-xe"),
        (4, "server-mgmt-01", "server-mgmt-01.lan", "Dell PowerEdge R740", "linux")
    ''')
    
    # Insert sample ports with MAC addresses
    conn.execute('''INSERT INTO ports (port_id, device_id, ifDescr, ifPhysAddress, ifOperStatus) VALUES
        (1, 1, "GigabitEthernet1/0/1", "001122334455", "up"),
        (2, 1, "GigabitEthernet1/0/2", "001122334456", "up"),
        (3, 1, "GigabitEthernet1/0/3", "aabbccddeeff", "down"),
        (4, 2, "FastEthernet0/1", "deadbeef0001", "up"),
        (5, 2, "FastEthernet0/2", "deadbeef0002", "up"),
        (6, 3, "GigabitEthernet0/0/0", "cafebabe1234", "up"),
        (7, 4, "eth0", "ffeeddccbbaa", "up"),
        (8, 4, "eth1", "112233445566", "up")
    ''')
    
    # Store the flag in secrets table
    conn.execute(f'INSERT INTO secrets (id, name, value) VALUES (1, "api_key", "{flag}")')
    conn.execute('INSERT INTO secrets (id, name, value) VALUES (2, "backup_key", "not-the-flag-keep-looking")')
    
    conn.commit()
    conn.close()


@app.post("/login")
async def login(request: Request):
    """Handle login and create session"""
    data = await request.json()
    username = data.get("username", "")
    password = data.get("password", "")
    
    if username in USERS and USERS[username] == password:
        # Create session
        session_id = secrets.token_hex(16)
        sessions[session_id] = {"username": username}
        
        response = JSONResponse(content={"success": True, "message": f"Welcome, {username}!"})
        response.set_cookie(key="session_id", value=session_id)
        return response
    
    return JSONResponse(content={"success": False, "error": "Invalid credentials"}, status_code=401)


@app.get("/logout")
async def logout(session_id: str = Cookie(default=None)):
    """Handle logout"""
    if session_id and session_id in sessions:
        del sessions[session_id]
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="session_id")
    return response


@app.post("/ajax/table/address-search")
async def address_search(request: Request, session_id: str = Cookie(default=None)):
    """
    MAC address search functionality - mimics LibreNMS's vulnerable endpoint.
    CVE-2023-5591: SQL injection via improper parameterization of MAC address search.
    """
    # Check authentication (CVE requires authenticated access)
    user = check_auth(session_id)
    if not user:
        return JSONResponse(
            content={"error": "Authentication required. Please login first."},
            status_code=401
        )
    
    data = await request.json()
    address = data.get("address", "")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Vulnerable code pattern from CVE-2023-5591:
    # The MAC address is processed to remove common separators,
    # but the result is directly interpolated into the SQL query
    # instead of being properly parameterized.
    
    # Apply the same transformations as the original vulnerable code:
    # trim(str_replace([':', ' ', '-', '.', '0x'], '', $vars['address']))
    cleaned_address = address.strip()
    for char in [':', ' ', '-', '.', '0x']:
        cleaned_address = cleaned_address.replace(char, '')
    
    # VULNERABLE: Direct string interpolation into SQL LIKE clause
    # This is the exact vulnerability pattern from CVE-2023-5591
    sql = f"SELECT I.port_id, I.ifDescr, I.ifPhysAddress, I.ifOperStatus, D.hostname, D.sysName " \
          f"FROM ports I, devices D " \
          f"WHERE I.device_id = D.device_id AND ifPhysAddress LIKE '%{cleaned_address}%'"
    
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        
        return {
            "data": [
                {
                    "port_id": row["port_id"],
                    "ifDescr": row["ifDescr"],
                    "ifPhysAddress": row["ifPhysAddress"],
                    "ifOperStatus": row["ifOperStatus"],
                    "hostname": row["hostname"],
                    "sysName": row["sysName"]
                }
                for row in results
            ]
        }
    except Exception as e:
        conn.close()
        # Return error message which can help with blind SQL injection
        return JSONResponse(
            content={"error": f"Database error: {str(e)}"},
            status_code=500
        )


@app.get("/api/devices")
async def list_devices(session_id: str = Cookie(default=None)):
    """List all network devices (requires authentication)"""
    user = check_auth(session_id)
    if not user:
        return JSONResponse(
            content={"error": "Authentication required"},
            status_code=401
        )
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices")
    devices = cursor.fetchall()
    conn.close()
    
    return {
        "devices": [
            {
                "device_id": d["device_id"],
                "hostname": d["hostname"],
                "sysName": d["sysName"],
                "hardware": d["hardware"],
                "os": d["os"]
            }
            for d in devices
        ]
    }


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

