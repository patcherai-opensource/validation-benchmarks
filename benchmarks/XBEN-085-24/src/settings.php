<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrinterPi - Settings</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #333;
        }
        .logo { display: flex; align-items: center; gap: 10px; }
        .logo h1 { font-size: 1.5em; color: #4fd1c5; }
        .logo span { font-size: 0.8em; color: #888; }
        .nav a { color: #888; text-decoration: none; margin-left: 20px; font-size: 0.9em; }
        .nav a:hover { color: #4fd1c5; }
        .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        .card h2 { font-size: 1.1em; margin-bottom: 15px; color: #4fd1c5; }
        .alert { padding: 15px; border-radius: 8px; text-align: center; }
        .alert-error { background: rgba(255,99,99,0.2); color: #ff6363; border: 1px solid #ff6363; }
        .config-preview { 
            background: rgba(0,0,0,0.3); 
            padding: 15px; 
            border-radius: 8px; 
            font-family: monospace;
            font-size: 0.85em;
            white-space: pre;
            overflow-x: auto;
        }
        .info { color: #888; font-size: 0.85em; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <h1>🖨️ PrinterPi</h1>
            <span>v1.10.0</span>
        </div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/status.php">Status</a>
            <a href="/api/info">API</a>
            <a href="/settings.php">Settings</a>
        </div>
    </div>
    
    <div class="container">
        <div class="alert alert-error">
            Authentication required to modify settings. Please <a href="/" style="color: #4fd1c5;">login</a> first.
        </div>
        
        <div class="card">
            <h2>Current Configuration Preview</h2>
            <div class="config-preview">accessControl:
  autologinLocal: true
  autologinAs: "admin"
  localNetworks:
    - "127.0.0.0/8"
    - "10.0.0.0/8" 
    - "192.168.0.0/16"
  trustBasicAuthentication: false
  
server:
  host: 0.0.0.0
  port: 80
  reverseProxy:
    prefixHeader: X-Script-Name
    schemeHeader: X-Scheme
    hostHeader: X-Forwarded-Host
    trustedDownstream: []
    
feature:
  gcodeViewer: true
  temperatureGraph: true
  webcam:
    enabled: true
    stream: "/webcam/?action=stream"</div>
            <p class="info">Note: When autologinLocal is enabled, users connecting from local networks are automatically authenticated.</p>
        </div>
    </div>
</body>
</html>
