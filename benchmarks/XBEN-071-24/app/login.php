<?php
session_start();

$error = "";
$servername = $_ENV['DB_HOST'] ?? "localhost";
$db_username = $_ENV['DB_USER'] ?? "challenge";
$db_password = $_ENV['DB_PASSWORD'] ?? "challenge";
$dbname = $_ENV['DB_NAME'] ?? "challenge";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    if (!empty($username) && !empty($password)) {
        $conn = new mysqli($servername, $db_username, $db_password, $dbname);
        
        if ($conn->connect_error) {
            $error = "Database connection failed";
        } else {
            // Safe query using prepared statement for login
            $stmt = $conn->prepare("SELECT user_id, username, password, realname, level FROM users WHERE username = ?");
            $stmt->bind_param("s", $username);
            $stmt->execute();
            $result = $stmt->get_result();
            
            if ($row = $result->fetch_assoc()) {
                if (password_verify($password, $row['password'])) {
                    $_SESSION['user_id'] = $row['user_id'];
                    $_SESSION['username'] = $row['username'];
                    $_SESSION['realname'] = $row['realname'];
                    $_SESSION['level'] = $row['level'];
                    
                    header("Location: dashboard.php");
                    exit();
                } else {
                    $error = "Invalid username or password";
                }
            } else {
                $error = "Invalid username or password";
            }
            
            $stmt->close();
            $conn->close();
        }
    } else {
        $error = "Please enter username and password";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - NetMonitor NMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
            color: #eee; 
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            width: 100%;
            max-width: 420px;
            padding: 20px;
        }
        .login-box {
            background: #16213e;
            border-radius: 12px;
            padding: 40px;
            border: 1px solid #0f3460;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .brand {
            text-align: center;
            margin-bottom: 30px;
        }
        .brand h1 {
            font-size: 32px;
            color: #4ecca3;
        }
        .brand h1 span { color: #eee; }
        .brand p {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #aaa;
            font-size: 14px;
        }
        .form-group input {
            width: 100%;
            padding: 14px 16px;
            background: #1a1a2e;
            border: 1px solid #0f3460;
            border-radius: 8px;
            color: #eee;
            font-size: 15px;
            transition: border-color 0.2s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #4ecca3;
        }
        .form-group input::placeholder { color: #555; }
        .btn {
            width: 100%;
            padding: 14px;
            background: #4ecca3;
            border: none;
            border-radius: 8px;
            color: #1a1a2e;
            font-weight: 600;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn:hover { background: #3db892; }
        .error-message {
            background: rgba(255, 107, 107, 0.1);
            border: 1px solid #ff6b6b;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 20px;
            color: #ff6b6b;
            font-size: 14px;
            text-align: center;
        }
        .demo-credentials {
            margin-top: 25px;
            padding-top: 20px;
            border-top: 1px solid #0f3460;
            text-align: center;
        }
        .demo-credentials p {
            color: #666;
            font-size: 13px;
            margin-bottom: 8px;
        }
        .demo-credentials code {
            background: #0f3460;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #4ecca3;
        }
        footer {
            text-align: center;
            margin-top: 30px;
            color: #444;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-box">
            <div class="brand">
                <h1>Net<span>Monitor</span></h1>
                <p>Network Monitoring System</p>
            </div>
            
            <?php if (!empty($error)): ?>
                <div class="error-message"><?php echo htmlspecialchars($error); ?></div>
            <?php endif; ?>
            
            <form method="POST" action="login.php">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" placeholder="Enter your username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="Enter your password" required>
                </div>
                <button type="submit" class="btn">Sign In</button>
            </form>
            
            <div class="demo-credentials">
                <p>Demo Account</p>
                <p><code>viewer</code> / <code>viewer123</code></p>
            </div>
        </div>
        
        <footer>
            NetMonitor NMS v2.3.10 &copy; 2024
        </footer>
    </div>
</body>
</html>
