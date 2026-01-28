<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - DeepVision</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <img src="images/logo.png" width="120" height="100">
        </div>
        <ul>
            <li><a href="/index.php">Home</a></li>
            <li><a href="/docs.php">API Docs</a></li>
            <li><a href="/models.php">Models</a></li>
            <li><a href="/datasets.php">Datasets</a></li>
            <li><a href="/login.php">Login</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>Developer Login</h1>
        <p>Access your DeepVision dashboard to manage API keys and view usage statistics.</p>
        <?php
        $showError = false;
        if ($_SERVER["REQUEST_METHOD"] == "POST") {
            $username = htmlspecialchars($_POST['username']);
            $password = htmlspecialchars($_POST['password']);
            
            $showError = true;
        }
        ?>
        <form action="login.php" method="post">
            <label for="username">Email:</label>
            <input type="text" id="username" name="username" required placeholder="developer@example.com">
            
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
            
            <input type="submit" value="Sign In">
        </form>
        <?php
        if ($showError) {
            echo "<p class='error'>Invalid credentials. Please try again.</p>";
        }
        ?>
        <p style="margin-top: 20px;">
            <a href="#">Forgot password?</a> | <a href="#">Create account</a>
        </p>
    </div>
</body>
</html>

