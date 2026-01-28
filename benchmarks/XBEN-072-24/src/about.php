<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudPanel - About</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            padding: 40px;
            width: 100%;
            max-width: 600px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #0f3460;
            font-size: 28px;
            margin-bottom: 5px;
        }
        .logo p {
            color: #666;
            font-size: 14px;
        }
        .nav-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
        }
        .nav-links a {
            color: #0f3460;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 4px;
            transition: background 0.3s;
        }
        .nav-links a:hover, .nav-links a.active {
            background: #e8f0fe;
        }
        h2 {
            color: #0f3460;
            margin-bottom: 20px;
            font-size: 20px;
        }
        p {
            color: #555;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .features {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .features h3 {
            color: #0f3460;
            margin-bottom: 15px;
        }
        .features ul {
            list-style: none;
            padding: 0;
        }
        .features li {
            padding: 8px 0;
            color: #555;
            border-bottom: 1px solid #eee;
        }
        .features li:last-child {
            border-bottom: none;
        }
        .version-info {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
        }
        .version-info strong {
            color: #856404;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>CloudPanel</h1>
            <p>Hosting Control Panel v2.1.1</p>
        </div>
        
        <div class="nav-links">
            <a href="index.php">Register</a>
            <a href="login.php">Login</a>
            <a href="about.php" class="active">About</a>
        </div>
        
        <h2>About CloudPanel</h2>
        
        <p>CloudPanel is a modern, lightweight hosting control panel designed for 
        managing web hosting accounts, domains, and server resources efficiently.</p>
        
        <div class="features">
            <h3>Key Features</h3>
            <ul>
                <li>✓ Customer self-registration portal</li>
                <li>✓ Domain and hosting management</li>
                <li>✓ SSL certificate provisioning</li>
                <li>✓ Email account management</li>
                <li>✓ Database administration</li>
                <li>✓ FTP account management</li>
                <li>✓ Resource usage monitoring</li>
            </ul>
        </div>
        
        <div class="version-info">
            <strong>Current Version:</strong> 2.1.1<br>
            <strong>Release Date:</strong> November 2024<br>
            <strong>PHP Version:</strong> <?php echo phpversion(); ?>
        </div>
        
        <p style="margin-top: 20px; font-size: 13px; color: #888;">
            For support inquiries, please contact your system administrator or 
            visit our documentation portal.
        </p>
        
        <div class="footer">
            <p>&copy; 2024 CloudPanel Hosting Solutions</p>
        </div>
    </div>
</body>
</html>
