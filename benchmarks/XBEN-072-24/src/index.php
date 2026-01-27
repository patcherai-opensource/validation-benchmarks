<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProcessKit - Shell Command Utility</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e8e8e8;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        header h1 {
            font-size: 2.5rem;
            color: #00d4ff;
            margin-bottom: 10px;
        }
        header p {
            color: #888;
            font-size: 1.1rem;
        }
        .card {
            background: #0f3460;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        .card h2 {
            color: #00d4ff;
            margin-bottom: 20px;
            font-size: 1.3rem;
            border-bottom: 1px solid #1a4a7a;
            padding-bottom: 10px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #aaa;
            font-size: 0.9rem;
        }
        input[type="text"], select {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid #1a4a7a;
            border-radius: 8px;
            background: #16213e;
            color: #e8e8e8;
            font-size: 1rem;
        }
        input[type="text"]:focus, select:focus {
            outline: none;
            border-color: #00d4ff;
        }
        button {
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            color: #000;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 212, 255, 0.3);
        }
        .output-section {
            margin-top: 20px;
        }
        .output-box {
            background: #0a0a15;
            border: 1px solid #1a4a7a;
            border-radius: 8px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            color: #0f0;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 400px;
            overflow-y: auto;
        }
        .error {
            color: #ff4444;
        }
        .info-box {
            background: #1a4a7a;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            font-size: 0.85rem;
            color: #aaa;
        }
        .info-box strong {
            color: #00d4ff;
        }
        .nav-links {
            text-align: center;
            margin-bottom: 20px;
        }
        .nav-links a {
            color: #00d4ff;
            margin: 0 15px;
            text-decoration: none;
        }
        .nav-links a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚙️ ProcessKit</h1>
            <p>System Process & Network Diagnostic Utility</p>
        </header>
        
        <div class="nav-links">
            <a href="index.php">Home</a>
            <a href="index.php?page=ping">Network Ping</a>
            <a href="index.php?page=dns">DNS Lookup</a>
            <a href="index.php?page=about">About</a>
        </div>

<?php
$page = isset($_GET['page']) ? $_GET['page'] : 'home';

if ($page === 'about') {
    echo '
        <div class="card">
            <h2>About ProcessKit</h2>
            <p>ProcessKit is a web-based utility for running common system diagnostics.</p>
            <p style="margin-top: 15px;">Version: 1.2.3</p>
            <p>Built with PHP Process Component</p>
            <div class="info-box">
                <strong>Note:</strong> This tool uses shell execution to run diagnostic commands.
                Ensure proper input validation in production environments.
            </div>
        </div>';
} elseif ($page === 'ping') {
?>
        <div class="card">
            <h2>🌐 Network Ping Utility</h2>
            <form method="POST" action="index.php?page=ping">
                <div class="form-group">
                    <label for="host">Target Host (IP or hostname):</label>
                    <input type="text" id="host" name="host" placeholder="e.g., 8.8.8.8 or google.com" 
                           value="<?php echo isset($_POST['host']) ? htmlspecialchars($_POST['host']) : ''; ?>">
                </div>
                <button type="submit">Run Ping</button>
            </form>
            
            <?php
            if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['host'])) {
                $host = $_POST['host'];
                
                if (empty($host)) {
                    echo '<div class="output-section"><div class="output-box error">Error: Please provide a host address.</div></div>';
                } else {
                    // Vulnerable: User input passed directly to shell command
                    // Simulating the CVE where command execution path is not properly secured
                    $cmd = "ping -c 3 " . $host;
                    
                    echo '<div class="output-section">';
                    echo '<h3 style="color:#00d4ff; margin-bottom:10px;">Command Output:</h3>';
                    echo '<div class="output-box">';
                    echo "$ " . htmlspecialchars($cmd) . "\n\n";
                    
                    $output = shell_exec($cmd . " 2>&1");
                    echo htmlspecialchars($output);
                    
                    echo '</div></div>';
                }
            }
            ?>
            
            <div class="info-box">
                <strong>Usage:</strong> Enter a valid IP address or hostname to check network connectivity.
                Example: <code>192.168.1.1</code> or <code>example.com</code>
            </div>
        </div>
<?php
} elseif ($page === 'dns') {
?>
        <div class="card">
            <h2>🔍 DNS Lookup</h2>
            <form method="POST" action="index.php?page=dns">
                <div class="form-group">
                    <label for="domain">Domain Name:</label>
                    <input type="text" id="domain" name="domain" placeholder="e.g., example.com"
                           value="<?php echo isset($_POST['domain']) ? htmlspecialchars($_POST['domain']) : ''; ?>">
                </div>
                <div class="form-group">
                    <label for="record_type">Record Type:</label>
                    <select id="record_type" name="record_type">
                        <option value="A" <?php echo (isset($_POST['record_type']) && $_POST['record_type'] === 'A') ? 'selected' : ''; ?>>A (Address)</option>
                        <option value="MX" <?php echo (isset($_POST['record_type']) && $_POST['record_type'] === 'MX') ? 'selected' : ''; ?>>MX (Mail)</option>
                        <option value="NS" <?php echo (isset($_POST['record_type']) && $_POST['record_type'] === 'NS') ? 'selected' : ''; ?>>NS (Nameserver)</option>
                        <option value="TXT" <?php echo (isset($_POST['record_type']) && $_POST['record_type'] === 'TXT') ? 'selected' : ''; ?>>TXT (Text)</option>
                    </select>
                </div>
                <button type="submit">Lookup DNS</button>
            </form>
            
            <?php
            if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['domain'])) {
                $domain = $_POST['domain'];
                $record_type = isset($_POST['record_type']) ? $_POST['record_type'] : 'A';
                
                // Basic validation for record type (whitelist)
                $allowed_types = ['A', 'MX', 'NS', 'TXT'];
                if (!in_array($record_type, $allowed_types)) {
                    $record_type = 'A';
                }
                
                if (empty($domain)) {
                    echo '<div class="output-section"><div class="output-box error">Error: Please provide a domain name.</div></div>';
                } else {
                    // Vulnerable: Domain input not sanitized
                    $cmd = "nslookup -type=" . $record_type . " " . $domain;
                    
                    echo '<div class="output-section">';
                    echo '<h3 style="color:#00d4ff; margin-bottom:10px;">DNS Lookup Results:</h3>';
                    echo '<div class="output-box">';
                    echo "$ " . htmlspecialchars($cmd) . "\n\n";
                    
                    $output = shell_exec($cmd . " 2>&1");
                    echo htmlspecialchars($output);
                    
                    echo '</div></div>';
                }
            }
            ?>
            
            <div class="info-box">
                <strong>Usage:</strong> Enter a domain name to query DNS records.
            </div>
        </div>
<?php
} else {
    // Home page
?>
        <div class="card">
            <h2>🏠 Welcome to ProcessKit</h2>
            <p>Select a diagnostic tool from the navigation above:</p>
            <ul style="margin: 20px 0; padding-left: 20px; line-height: 2;">
                <li><a href="index.php?page=ping" style="color:#00d4ff;">Network Ping</a> - Test connectivity to remote hosts</li>
                <li><a href="index.php?page=dns" style="color:#00d4ff;">DNS Lookup</a> - Query DNS records for domains</li>
            </ul>
            <div class="info-box">
                <strong>System Info:</strong><br>
                PHP Version: <?php echo phpversion(); ?><br>
                Server: <?php echo $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'; ?>
            </div>
        </div>
<?php
}
?>
    </div>
</body>
</html>

