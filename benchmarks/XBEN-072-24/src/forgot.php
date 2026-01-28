<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudPanel - Password Recovery</title>
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
            max-width: 400px;
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
        h2 {
            color: #0f3460;
            text-align: center;
            margin-bottom: 25px;
            font-size: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
            font-size: 14px;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        .btn {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            background: #3498db;
            color: white;
        }
        .message {
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            text-align: center;
            background: #d4edda;
            color: #155724;
        }
        .links {
            text-align: center;
            margin-top: 20px;
        }
        .links a {
            color: #3498db;
            text-decoration: none;
            font-size: 14px;
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
<?php
$message = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['reset'])) {
    $message = 'If an account exists with that email, a password reset link has been sent.';
}
?>
    <div class="container">
        <div class="logo">
            <h1>CloudPanel</h1>
            <p>Hosting Control Panel v2.1.1</p>
        </div>
        
        <h2>Password Recovery</h2>
        
        <?php if ($message): ?>
        <div class="message">
            <?php echo htmlspecialchars($message); ?>
        </div>
        <?php endif; ?>
        
        <form action="forgot.php" method="POST">
            <div class="form-group">
                <label>Email Address</label>
                <input type="email" name="email" placeholder="john@example.com" required>
            </div>
            
            <button type="submit" name="reset" class="btn">Send Reset Link</button>
        </form>
        
        <div class="links">
            <a href="login.php">Back to Login</a>
        </div>
        
        <div class="footer">
            <p>&copy; 2024 CloudPanel Hosting Solutions</p>
        </div>
    </div>
</body>
</html>
