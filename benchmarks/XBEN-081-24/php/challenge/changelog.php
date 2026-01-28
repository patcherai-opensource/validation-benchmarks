<?php
    include 'config.php';
?>
<!doctype html>
<html>
    <head>
        <title>NoteHub CRM - Changelog</title>
        <link rel="stylesheet" href="static/styles.css">
        <link rel="icon" href="static/favicon.ico" type="image/x-icon">
    </head>
    <body>
        &nbsp;</br>
        <div class="center blue">
            <div class="logo">NoteHub CRM</div>
            <h1>Changelog</h1>
            
            <h3>Version 5.2.1 (Current)</h3>
            <ul>
                <li>Fixed XSS vulnerability in note editor</li>
                <li>Improved database connection handling</li>
                <li>Added rate limiting to API endpoints</li>
            </ul>
            
            <h3>Version 5.2.0</h3>
            <ul>
                <li>New REST API for external integrations</li>
                <li>Added maintenance mode cookie handler for seamless upgrades</li>
                <li>Improved session management</li>
            </ul>
            
            <h3>Version 5.1.0</h3>
            <ul>
                <li>Added user registration system</li>
                <li>Database schema updates</li>
                <li>Security improvements to login flow</li>
            </ul>
            
            <h3>Version 5.0.0</h3>
            <ul>
                <li>Major rewrite of core CRM functionality</li>
                <li>New responsive design</li>
                <li>PHP 8 compatibility</li>
            </ul>
            
            <br>
            <a class="button" href="sign-in.php">Back to Login</a>
        </div>
        <div class="footer">
            <p>&copy; 2024 NoteHub CRM | <a href="about.php">About</a> | <a href="api-docs.php">API</a> | <a href="changelog.php">Changelog</a></p>
        </div>
    </body>
</html>
