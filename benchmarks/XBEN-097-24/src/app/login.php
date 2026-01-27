<?php
/**
 * OpenWiki - Login Page
 */
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenWiki - Login</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="wiki-header">
        <div class="logo">
            <h1><a href="/">OpenWiki</a></h1>
            <span class="tagline">Collaborative Knowledge Platform</span>
        </div>
        <nav class="main-nav">
            <ul>
                <li><a href="/?page=HomePage">Home</a></li>
                <li><a href="/?page=Documentation">Docs</a></li>
                <li><a href="/?page=RecentChanges">Recent Changes</a></li>
            </ul>
        </nav>
    </header>

    <div class="wiki-container">
        <aside class="sidebar">
            <div class="widget">
                <h3>Navigation</h3>
                <ul>
                    <li><a href="/?page=HomePage">Home</a></li>
                    <li><a href="/?page=SiteMap">Site Map</a></li>
                </ul>
            </div>
        </aside>

        <main class="content">
            <article class="wiki-page">
                <h2>User Login</h2>
                
                <?php
                $showError = false;
                if ($_SERVER["REQUEST_METHOD"] == "POST") {
                    $username = htmlspecialchars($_POST['username']);
                    $password = htmlspecialchars($_POST['password']);
                    $showError = true;
                }
                ?>
                
                <div class="page-content">
                    <p>Please enter your credentials to access your OpenWiki account.</p>
                    
                    <form action="login.php" method="post">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" required>
                        
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required>
                        
                        <input type="submit" value="Login">
                    </form>
                    
                    <?php if ($showError): ?>
                    <p class="error">Invalid username or password. Please try again.</p>
                    <?php endif; ?>
                    
                    <p style="margin-top: 20px;">
                        <a href="/?page=PasswordRecovery">Forgot your password?</a> |
                        <a href="/?page=UserRegistration">Create new account</a>
                    </p>
                </div>
            </article>
        </main>
    </div>

    <footer class="wiki-footer">
        <p>&copy; 2024 OpenWiki. Powered by OpenWiki v4.2.1</p>
    </footer>
</body>
</html>

