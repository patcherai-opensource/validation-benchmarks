<?php
session_start();

// Database connection helper
function getDbConnection() {
    $servername = $_ENV['DB_HOST'] ?? "localhost";
    $username = $_ENV['DB_USER'] ?? "challenge";
    $password = $_ENV['DB_PASSWORD'] ?? "challenge";
    $dbname = $_ENV['DB_NAME'] ?? "challenge";
    
    $conn = new mysqli($servername, $username, $password, $dbname);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    return $conn;
}

$login_error = "";

// Handle login
if (isset($_POST['action']) && $_POST['action'] === 'login') {
    $conn = getDbConnection();
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    $stmt = $conn->prepare("SELECT id, username, password FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($row = $result->fetch_assoc()) {
        if (password_verify($password, $row['password'])) {
            $_SESSION['user_id'] = $row['id'];
            $_SESSION['username'] = $row['username'];
            header("Location: admin.php");
            exit;
        }
    }
    
    $login_error = "Invalid username or password";
    $conn->close();
}

// Handle logout
if (isset($_GET['logout'])) {
    session_destroy();
    header("Location: send.php");
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - KnowledgeBase Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #1e3a5f;
            font-size: 24px;
        }
        .logo p {
            color: #666;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #1e3a5f;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: #1e3a5f;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #2d5a8a;
        }
        .error {
            background: #fee;
            color: #c00;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .info-box {
            margin-top: 20px;
            padding: 15px;
            background: #f0f7ff;
            border-radius: 5px;
            font-size: 13px;
            color: #444;
        }
        .info-box strong {
            color: #1e3a5f;
        }
        a { color: #1e3a5f; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>📚 KnowledgeBase Pro</h1>
            <p>Administration Panel</p>
        </div>
        
        <?php if ($login_error): ?>
            <div class="error"><?php echo htmlspecialchars($login_error); ?></div>
        <?php endif; ?>
        
        <form method="POST" action="send.php">
            <input type="hidden" name="action" value="login">
            
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn">Sign In</button>
        </form>
        
        <div class="info-box">
            <strong>Note:</strong> This is the admin area. Regular users please visit the <a href="index.html">public FAQ page</a>.
        </div>
    </div>
</body>
</html>
