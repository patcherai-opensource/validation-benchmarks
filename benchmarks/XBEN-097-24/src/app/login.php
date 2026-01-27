<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign In - DataAnnotate</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <script src="/static/js/app.js"></script>
</head>
<body>
    <header class="header">
        <h1>DataAnnotate</h1>
        <nav class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/projects.php">Projects</a>
            <a href="/docs.php">Documentation</a>
            <a href="/login.php">Sign In</a>
        </nav>
    </header>
    
    <div class="container">
        <div class="login-form card">
            <h2>Sign In to DataAnnotate</h2>
            
            <?php
            $showError = false;
            if ($_SERVER["REQUEST_METHOD"] == "POST") {
                $email = htmlspecialchars($_POST['email']);
                $password = htmlspecialchars($_POST['password']);
                $showError = true;
            }
            
            if ($showError) {
                echo '<div class="error-message">Invalid email or password. Please try again.</div>';
            }
            ?>
            
            <form action="login.php" method="post">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" placeholder="user@example.com" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="Enter your password" required>
                </div>
                
                <button type="submit" class="btn" style="width: 100%;">Sign In</button>
            </form>
            
            <p style="text-align: center; margin-top: 20px; color: #666;">
                Don't have an account? <a href="/signup.php">Sign up</a>
            </p>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2024 DataAnnotate Platform v2.1.0</p>
    </footer>
</body>
</html>

