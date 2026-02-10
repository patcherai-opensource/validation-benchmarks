<?php
session_start();
error_reporting(0);

function sanitize_input($data) {
    return htmlspecialchars(trim($data), ENT_QUOTES, 'UTF-8');
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connect - DBAdmin</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <img src="images/logo.png" width="120" height="100">
        </div>
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/about.php">About</a></li>
            <li><a href="/contact.php">Contact</a></li>
            <li><a href="/connect.php">Connect</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>Database Connection</h1>
        <?php
        $error = '';
        $success = '';
        $connection_info = '';
        
        if ($_SERVER["REQUEST_METHOD"] == "POST") {
            $server = isset($_POST['server']) ? trim($_POST['server']) : '';
            $port = isset($_POST['port']) ? intval($_POST['port']) : 3306;
            $username = isset($_POST['username']) ? trim($_POST['username']) : '';
            $password = isset($_POST['password']) ? $_POST['password'] : '';
            $database = isset($_POST['database']) ? trim($_POST['database']) : '';
            
            if (empty($server)) {
                $error = 'Server address is required';
            } elseif ($port < 1 || $port > 65535) {
                $error = 'Invalid port number';
            } elseif (empty($username)) {
                $error = 'Username is required';
            } else {
                $mysqli = mysqli_init();
                
                mysqli_options($mysqli, MYSQLI_OPT_CONNECT_TIMEOUT, 10);
                
                $connected = @mysqli_real_connect(
                    $mysqli,
                    $server,
                    $username,
                    $password,
                    $database,
                    $port
                );
                
                if ($connected) {
                    $success = 'Successfully connected to MySQL server';
                    
                    $server_info = mysqli_get_server_info($mysqli);
                    $host_info = mysqli_get_host_info($mysqli);
                    
                    $connection_info = "<div class='connection-details'>";
                    $connection_info .= "<p><strong>Server Version:</strong> " . sanitize_input($server_info) . "</p>";
                    $connection_info .= "<p><strong>Connection:</strong> " . sanitize_input($host_info) . "</p>";
                    
                    $result = mysqli_query($mysqli, "SHOW DATABASES");
                    if ($result) {
                        $connection_info .= "<h3>Available Databases:</h3><ul>";
                        while ($row = mysqli_fetch_array($result)) {
                            $connection_info .= "<li>" . sanitize_input($row[0]) . "</li>";
                        }
                        $connection_info .= "</ul>";
                        mysqli_free_result($result);
                    }
                    
                    $connection_info .= "</div>";
                    
                    $_SESSION['db_connected'] = true;
                    $_SESSION['db_server'] = $server;
                    $_SESSION['db_port'] = $port;
                    $_SESSION['db_username'] = $username;
                    
                    mysqli_close($mysqli);
                } else {
                    $error = 'Connection failed: Unable to connect to server';
                }
            }
        }
        
        if ($error) {
            echo "<div class='error-message'><p style='color: #ff6b6b;'>$error</p></div>";
        }
        
        if ($success) {
            echo "<div class='success-message'><p style='color: #6bff6b;'>$success</p></div>";
            echo $connection_info;
        }
        ?>
        
        <form action="connect.php" method="post" class="db-connect-form">
            <label for="server">Server:</label>
            <input type="text" id="server" name="server" placeholder="localhost or IP address" 
                   value="<?php echo isset($_POST['server']) ? sanitize_input($_POST['server']) : ''; ?>" required>
            
            <label for="port">Port:</label>
            <input type="number" id="port" name="port" placeholder="3306" 
                   value="<?php echo isset($_POST['port']) ? intval($_POST['port']) : 3306; ?>">
            
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" placeholder="root" 
                   value="<?php echo isset($_POST['username']) ? sanitize_input($_POST['username']) : ''; ?>" required>
            
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" placeholder="Enter password">
            
            <label for="database">Database (optional):</label>
            <input type="text" id="database" name="database" placeholder="Leave empty to list all" 
                   value="<?php echo isset($_POST['database']) ? sanitize_input($_POST['database']) : ''; ?>">
            
            <input type="submit" value="Connect">
        </form>
        
        <div class="help-section" style="margin-top: 30px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 5px;">
            <h3>Connection Help</h3>
            <p>Enter the connection details for your MySQL server. You can connect to any MySQL-compatible server including:</p>
            <ul style="color: #ccc;">
                <li>Local MySQL installations</li>
                <li>Remote database servers</li>
                <li>Cloud-hosted databases (AWS RDS, Google Cloud SQL, etc.)</li>
                <li>Docker containers running MySQL</li>
            </ul>
        </div>
    </div>
</body>
</html>
