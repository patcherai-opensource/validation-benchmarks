<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Access Restricted</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f6fa; color: #2d3436; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .restricted-box { background: #fff; border-radius: 8px; padding: 2rem; width: 100%; max-width: 500px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .restricted-box h1 { color: #d63031; font-size: 1.5rem; margin-bottom: 1rem; }
        .restricted-box p { color: #636e72; margin-bottom: 0.5rem; }
        .ip-display { background: #f5f6fa; padding: 0.5rem 1rem; border-radius: 4px; display: inline-block; margin: 1rem 0; font-family: monospace; font-size: 0.9rem; }
        .back-link { margin-top: 1rem; }
        .back-link a { color: #0984e3; text-decoration: none; }
    </style>
</head>
<body>
    <div class="restricted-box">
        <h1>403 - Access Restricted</h1>
        <p>The administration panel is only accessible from authorized internal networks.</p>
        <div class="ip-display">Your IP: <?= htmlspecialchars($data['clientIP']) ?></div>
        <p>Contact your network administrator if you believe this is an error.</p>
        <div class="back-link">
            <a href="/">&larr; Back to Dashboard</a>
        </div>
    </div>
</body>
</html>
