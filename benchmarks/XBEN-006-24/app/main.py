import json
import os
import re

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
import sqlite3

app = FastAPI(title="NetMonitor - Network Device Management")


def get_db_connection():
    conn = sqlite3.connect('netmonitor.db')
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
    
    # Create devices table for normal network devices
    conn.execute('''CREATE TABLE IF NOT EXISTS devices (
        device_id INTEGER PRIMARY KEY,
        hostname TEXT,
        ip_address TEXT,
        status TEXT
    )''')
    
    # Create interfaces table that links to devices
    conn.execute('''CREATE TABLE IF NOT EXISTS interfaces (
        interface_id INTEGER PRIMARY KEY,
        device_id INTEGER,
        ifName TEXT,
        ifPhysAddress TEXT,
        ifAlias TEXT,
        FOREIGN KEY (device_id) REFERENCES devices(device_id)
    )''')
    
    # Create admin_configs table for sensitive data (flag stored here)
    conn.execute('''CREATE TABLE IF NOT EXISTS admin_configs (
        config_id INTEGER PRIMARY KEY,
        config_key TEXT,
        config_value TEXT
    )''')
    
    conn.execute('DELETE FROM devices')
    conn.execute('DELETE FROM interfaces')
    conn.execute('DELETE FROM admin_configs')
    
    # Insert sample devices
    conn.execute('''INSERT INTO devices (hostname, ip_address, status) VALUES 
        ("core-router-01", "192.168.1.1", "up"),
        ("switch-floor1", "192.168.1.10", "up"),
        ("switch-floor2", "192.168.1.11", "up"),
        ("firewall-main", "192.168.1.254", "up"),
        ("backup-server", "192.168.1.50", "down")
    ''')
    
    # Insert sample interfaces with MAC addresses
    conn.execute('''INSERT INTO interfaces (device_id, ifName, ifPhysAddress, ifAlias) VALUES 
        (1, "GigabitEthernet0/0", "001122334455", "Uplink to ISP"),
        (1, "GigabitEthernet0/1", "001122334456", "LAN Interface"),
        (2, "FastEthernet0/1", "aabbccddeeff", "Floor 1 Access"),
        (2, "FastEthernet0/24", "aabbccddef00", "Uplink"),
        (3, "FastEthernet0/1", "112233445566", "Floor 2 Access"),
        (4, "eth0", "deadbeefcafe", "External"),
        (4, "eth1", "cafebabe1234", "Internal"),
        (5, "bond0", "ffeeddccbbaa", "Management")
    ''')
    
    # Store the flag in admin_configs table
    conn.execute(f'''INSERT INTO admin_configs (config_key, config_value) VALUES 
        ("system_name", "NetMonitor Pro"),
        ("admin_secret", "{flag}"),
        ("version", "2.4.1")
    ''')
    
    conn.commit()
    conn.close()


def sanitize_mac_input(address):
    """
    Sanitize MAC address input by removing common formatting characters.
    This mimics MAC address normalization - removing colons, dashes, dots, and 0x prefix.
    Note: This does NOT protect against SQL injection - it only normalizes MAC format.
    """
    if not address:
        return ""
    # Remove common MAC address formatting characters
    # Note: Spaces are preserved as they shouldn't appear in valid MAC addresses
    sanitized = address.replace(':', '').replace('-', '').replace('.', '').replace('0x', '')
    return sanitized


@app.post("/ajax/table")
async def address_search(request: Request):
    """
    AJAX endpoint for MAC address search - similar to LibreNMS address-search.inc.php
    """
    try:
        data = await request.json()
    except:
        return JSONResponse(content={"error": "Invalid JSON"}, status_code=400)
    
    table_id = data.get('id', '')
    address = data.get('address', '')
    
    # Only handle address-search table requests
    if table_id != 'address-search':
        return JSONResponse(content={"error": "Invalid table ID"}, status_code=400)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sanitize the MAC address input (remove formatting characters)
    # This is the vulnerable sanitization similar to CVE-2023-5591
    sanitized_address = sanitize_mac_input(address)
    
    # Vulnerable SQL query - direct interpolation into LIKE clause
    # Mimics: $sql .= " WHERE I.device_id = D.device_id AND `ifPhysAddress` LIKE '%" . trim(...) . "%' $where ";
    query = f"""
        SELECT I.interface_id, I.ifName, I.ifPhysAddress, I.ifAlias, D.hostname, D.ip_address 
        FROM interfaces I, devices D 
        WHERE I.device_id = D.device_id AND ifPhysAddress LIKE '%{sanitized_address}%'
    """
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return {
            "data": [
                {
                    "interface_id": row["interface_id"],
                    "ifName": row["ifName"],
                    "ifPhysAddress": row["ifPhysAddress"],
                    "ifAlias": row["ifAlias"],
                    "hostname": row["hostname"],
                    "ip_address": row["ip_address"]
                } for row in results
            ],
            "recordsTotal": len(results),
            "recordsFiltered": len(results)
        }
    except sqlite3.Error as e:
        conn.close()
        # Return SQL error for debugging (realistic behavior in dev/misconfigured systems)
        return JSONResponse(
            content={"error": f"Database error: {str(e)}"}, 
            status_code=500
        )


@app.get("/api/devices")
def list_devices():
    """List all monitored devices"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT device_id, hostname, ip_address, status FROM devices")
    devices = cursor.fetchall()
    conn.close()
    return [{"device_id": d["device_id"], "hostname": d["hostname"], 
             "ip_address": d["ip_address"], "status": d["status"]} for d in devices]


@app.get("/ping")
def ping():
    return {"status": "ok", "service": "netmonitor"}


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/search/mac", response_class=HTMLResponse)
def mac_search_page():
    """MAC Address Search Page - similar to LibreNMS search/mac.inc.php"""
    with open("static/mac-search.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

