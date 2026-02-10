<?php
session_start();

// Check if user is logged in
$logged_in = isset($_SESSION['user']);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RaspAP - Network Configuration</title>
    <link rel="stylesheet" type="text/css" href="static/styles.css">
</head>
<body>
    <div class="container">
        <h1>RaspAP Network Configuration</h1>
        
        <?php if (!$logged_in): ?>
            <h2>Login</h2>
            <form action="login.php" method="post">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p class="hint">Default credentials: admin / admin</p>
        <?php else: ?>
            <p>Welcome, <?php echo htmlspecialchars($_SESSION['user']); ?>!</p>
            <h2>WireGuard Key Management</h2>
            <p>Generate WireGuard keys for your VPN configuration.</p>
            <form action="ajax/networking/get_wgkey.php" method="post" id="wgkeyForm">
                <label for="entity">Entity Name:</label>
                <input type="text" name="entity" id="entity" placeholder="Enter entity name (e.g., wg0)" required>
                <button type="submit">Generate Keys</button>
            </form>
            <div id="result"></div>
            <br>
            <a href="logout.php">Logout</a>
        <?php endif; ?>
    </div>

    <script>
    document.getElementById('wgkeyForm')?.addEventListener('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(this);
        fetch('ajax/networking/get_wgkey.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        })
        .catch(error => {
            document.getElementById('result').innerHTML = '<pre>Error: ' + error + '</pre>';
        });
    });
    </script>
</body>
</html>
