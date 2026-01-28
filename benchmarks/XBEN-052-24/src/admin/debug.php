<?php
/**
 * EzContent CMS - Debug Information
 * WARNING: This page should be disabled in production
 */

// Simulate debug info - but don't reveal the flag or direct hints
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EzContent CMS - Debug</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a2e;
            color: #00ff00;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        h1 {
            color: #4caf50;
            border-bottom: 1px solid #4caf50;
            padding-bottom: 10px;
        }
        .debug-section {
            margin: 20px 0;
            padding: 15px;
            background: #0d0d1a;
            border: 1px solid #333;
            border-radius: 5px;
        }
        .debug-section h3 {
            color: #ff9800;
            margin-bottom: 10px;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .warning {
            color: #ff5722;
            padding: 10px;
            border: 1px solid #ff5722;
            margin-bottom: 20px;
        }
        a {
            color: #4caf50;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>[DEBUG] EzContent CMS v4.2.1</h1>
        
        <div class="warning">
            ⚠️ WARNING: Debug mode is enabled. Disable in production!
        </div>
        
        <div class="debug-section">
            <h3>Request Information</h3>
            <pre>
Request Method: <?php echo $_SERVER['REQUEST_METHOD']; ?>

Request URI: <?php echo $_SERVER['REQUEST_URI']; ?>

User Agent: <?php echo isset($_SERVER['HTTP_USER_AGENT']) ? htmlspecialchars($_SERVER['HTTP_USER_AGENT']) : 'N/A'; ?>

Remote IP: <?php echo $_SERVER['REMOTE_ADDR']; ?>

            </pre>
        </div>
        
        <div class="debug-section">
            <h3>Server Configuration</h3>
            <pre>
PHP Version: <?php echo phpversion(); ?>

Server Software: <?php echo $_SERVER['SERVER_SOFTWARE']; ?>

Document Root: <?php echo $_SERVER['DOCUMENT_ROOT']; ?>

            </pre>
        </div>
        
        <div class="debug-section">
            <h3>Login Handler Stack Trace (Last Request)</h3>
            <pre>
[2024-01-15 10:23:45] DEBUG kernel/classes/datatypes/ezuser/ezuserloginhandler.php
  > checkUser() called
  > Processing handlers: [standard, LDAP]
  
[2024-01-15 10:23:45] DEBUG kernel/classes/datatypes/ezuser/ezuser.php  
  > _loginUser() invoked
  > Login handler chain initialized
  > Checking user authentication...

[2024-01-15 10:23:45] INFO Authentication result: [REDACTED]
            </pre>
        </div>
        
        <div class="debug-section">
            <h3>Registered Users (Hash Types)</h3>
            <pre>
User: admin     | Role: administrator | Hash Type: 0 (external)
User: editor    | Role: editor        | Hash Type: 1 (md5)
User: guest     | Role: guest         | Hash Type: 1 (md5)

Note: Hash Type 0 = External authentication (LDAP/TextFile)
      Hash Type 1 = MD5 password hash
      Hash Type 2 = SHA256 password hash
            </pre>
        </div>
        
        <p><a href="/">&larr; Back to Login</a></p>
    </div>
</body>
</html>
