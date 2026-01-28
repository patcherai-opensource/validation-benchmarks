<?php
session_start();
?>
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel - AssetCore</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 400px; margin: 50px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: 600; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; background: #dc3545; color: white; padding: 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #c82333; }
        .error { color: #dc3545; text-align: center; margin: 10px 0; }
        .info { color: #666; font-size: 12px; text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Admin Login</h1>
        
        <?php
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            $username = isset($_POST['username']) ? $_POST['username'] : '';
            $password = isset($_POST['password']) ? $_POST['password'] : '';
            
            // Secure authentication with prepared statements
            $servername = getenv('MYSQL_HOST');
            $db_user = getenv('MYSQL_USER');
            $db_pass = getenv('MYSQL_PASSWORD');
            $dbname = getenv('MYSQL_DATABASE');
            
            $conn = new mysqli($servername, $db_user, $db_pass, $dbname);
            
            if (!$conn->connect_error) {
                $stmt = $conn->prepare("SELECT * FROM users WHERE username = ? AND password_hash = ?");
                $hash = md5($password);
                $stmt->bind_param("ss", $username, $hash);
                $stmt->execute();
                $result = $stmt->get_result();
                
                if ($result->num_rows > 0) {
                    $_SESSION['admin'] = true;
                    echo '<div class="error">Feature under development. Access denied.</div>';
                } else {
                    echo '<div class="error">Invalid credentials</div>';
                }
                $stmt->close();
                $conn->close();
            }
        }
        ?>
        
        <form method="POST" action="">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Sign In</button>
        </form>
        
        <p class="info">Admin access is restricted to authorized personnel only.</p>
        <p class="info"><a href="/index.php">← Back to Home</a></p>
    </div>
</body>
</html>
