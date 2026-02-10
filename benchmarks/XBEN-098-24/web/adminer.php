<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Admin - Connect</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <img src="images/logo.png" width="120" height="100">
        </div>
        <ul>
            <li><a href="/home.php">Home</a></li>
            <li><a href="/about.php">About</a></li>
            <li><a href="/contact.php">Contact</a></li>
            <li><a href="/login.php">Login</a></li>
            <li><a href="/adminer.php">DB Admin</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>Database Administration Tool</h1>
        <p>Connect to a MySQL database server to manage your data.</p>
        
        <?php
        $error = null;
        $success = null;
        
        if ($_SERVER["REQUEST_METHOD"] == "POST") {
            $host = isset($_POST['host']) ? $_POST['host'] : 'localhost';
            $port = isset($_POST['port']) ? intval($_POST['port']) : 3306;
            $username = isset($_POST['username']) ? $_POST['username'] : '';
            $password = isset($_POST['password']) ? $_POST['password'] : '';
            $database = isset($_POST['database']) ? $_POST['database'] : '';
            
            if (empty($host)) {
                $error = "Server hostname is required";
            } else {
                // Attempt to connect to the MySQL server
                // Note: This is vulnerable to LOAD DATA LOCAL INFILE attacks
                // because we don't disable the LOCAL_INFILE option
                try {
                    // Create connection with mysqli
                    // The vulnerability is here - we don't set MYSQLI_OPT_LOCAL_INFILE to false
                    $mysqli = new mysqli();
                    
                    // Enable LOCAL INFILE (this is the vulnerability!)
                    $mysqli->options(MYSQLI_OPT_LOCAL_INFILE, true);
                    
                    // Attempt connection
                    $mysqli->real_connect($host, $username, $password, $database, $port);
                    
                    if ($mysqli->connect_errno) {
                        $error = "Connection failed: " . $mysqli->connect_error;
                    } else {
                        $success = "Successfully connected to database server at $host:$port";
                        
                        // Try to get server version
                        $result = $mysqli->query("SELECT VERSION()");
                        if ($result) {
                            $row = $result->fetch_row();
                            $success .= "<br>Server version: " . htmlspecialchars($row[0]);
                        }
                        
                        $mysqli->close();
                    }
                } catch (Exception $e) {
                    $error = "Connection error: " . $e->getMessage();
                }
            }
        }
        ?>
        
        <form action="adminer.php" method="post" class="db-connect-form">
            <div class="form-group">
                <label for="host">Server:</label>
                <input type="text" id="host" name="host" placeholder="localhost" 
                       value="<?php echo isset($_POST['host']) ? htmlspecialchars($_POST['host']) : ''; ?>">
            </div>
            
            <div class="form-group">
                <label for="port">Port:</label>
                <input type="number" id="port" name="port" placeholder="3306" 
                       value="<?php echo isset($_POST['port']) ? htmlspecialchars($_POST['port']) : '3306'; ?>">
            </div>
            
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" placeholder="root"
                       value="<?php echo isset($_POST['username']) ? htmlspecialchars($_POST['username']) : ''; ?>">
            </div>
            
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password">
            </div>
            
            <div class="form-group">
                <label for="database">Database (optional):</label>
                <input type="text" id="database" name="database"
                       value="<?php echo isset($_POST['database']) ? htmlspecialchars($_POST['database']) : ''; ?>">
            </div>
            
            <input type="submit" value="Connect">
        </form>
        
        <?php if ($error): ?>
            <div class="error-message">
                <p>Error: <?php echo htmlspecialchars($error); ?></p>
            </div>
        <?php endif; ?>
        
        <?php if ($success): ?>
            <div class="success-message">
                <p><?php echo $success; ?></p>
            </div>
        <?php endif; ?>
        
        <div class="info-box">
            <h3>About this tool</h3>
            <p>This is a lightweight database administration interface. Enter your MySQL server details above to connect and manage your database.</p>
            <p><strong>Note:</strong> Make sure your MySQL server is accessible from this server.</p>
            <p><em>Internal MySQL server available at localhost:3306</em></p>
        </div>
    </div>
</body>
</html>
