<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrinterPi - Status</title>
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
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        .card h2 { font-size: 1.1em; margin-bottom: 15px; color: #4fd1c5; }
        .status-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .status-value { color: #4fd1c5; }
        pre { background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 0.85em; }
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
        <div class="card">
            <h2>Printer Status</h2>
            <div class="status-item">
                <span>State</span>
                <span class="status-value">Operational</span>
            </div>
            <div class="status-item">
                <span>Job Progress</span>
                <span class="status-value">N/A</span>
            </div>
            <div class="status-item">
                <span>Print Time</span>
                <span class="status-value">0:00:00</span>
            </div>
            <div class="status-item">
                <span>Estimated Time Left</span>
                <span class="status-value">N/A</span>
            </div>
        </div>
        
        <div class="card">
            <h2>Temperature Readings</h2>
            <div class="status-item">
                <span>Hotend (Tool 0)</span>
                <span class="status-value">205.2°C / 205°C</span>
            </div>
            <div class="status-item">
                <span>Bed</span>
                <span class="status-value">60.1°C / 60°C</span>
            </div>
            <div class="status-item">
                <span>Chamber</span>
                <span class="status-value">25.4°C</span>
            </div>
        </div>
        
        <div class="card">
            <h2>System Information</h2>
            <pre>
{
    "version": "1.10.0",
    "api_version": "2.0",
    "server_time": "<?php echo date('Y-m-d H:i:s'); ?>",
    "uptime": "3d 14h 22m",
    "python": "3.9.7",
    "pip": "21.2.4"
}
            </pre>
        </div>
    </div>
</body>
</html>
