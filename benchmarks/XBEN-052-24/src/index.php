<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Springfield CMS - Login</title>
    <style>
        body {
            background-color: #FFD90F;
            background-image: url('./static/springfield_background.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            font-family: 'Arial', sans-serif;
            text-align: center;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 0;
        }
        h1, h2, h3 {
            text-shadow: 2px 2px #000000;
            color: #FFFFFF;
        }
        .info-box {
            background-color: rgba(255,255,255,0.9);
            padding: 10px 20px;
            border-radius: 5px;
            margin-bottom: 10px;
            font-size: 12px;
            color: #333;
        }
        form {
            margin-top: 20px;
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 10px;
            display: inline-block;
            box-shadow: 0 0 10px #000000;
        }
        input[type="text"], input[type="password"] {
            margin: 10px 0;
            padding: 10px;
            width: 200px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            background-color: #6495ED;
            color: #FFFFFF;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #4169E1;
        }
        .error {
            color: #cc0000;
            background-color: #ffe6e6;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
        .success {
            color: #006600;
            background-color: #e6ffe6;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Springfield CMS</h1>
    <div class="info-box">
        Login Handlers: Standard + LDAP (Legacy Mode Enabled)<br>
        <small>Default admin account: admin</small>
    </div>
    <form action="index.php" method="POST">
        <label>Login:</label><br>
        <input type="text" name="login" placeholder="Username"><br>
        <label>Password:</label><br>
        <input type="password" name="password" placeholder="Password"><br>
        <button type="submit">Sign In</button>
    </form>
    <?php
        // Flag is embedded at build time
        $flag = "@FLAG@";
        
        // Initialize SQLite database
        $db_file = '/tmp/users.db';
        
        function initDatabase($db_file, $flag) {
            $db = new SQLite3($db_file);
            
            // Create users table mimicking eZ Publish user structure
            // password_hash_type: 0 = no password required, 1 = md5, 2 = sha1, etc.
            $db->exec('CREATE TABLE IF NOT EXISTS ezuser (
                contentobject_id INTEGER PRIMARY KEY,
                login TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT,
                password_hash_type INTEGER DEFAULT 1,
                is_enabled INTEGER DEFAULT 1,
                role TEXT DEFAULT "user"
            )');
            
            // Create secrets table for admin access
            $db->exec('CREATE TABLE IF NOT EXISTS admin_secrets (
                id INTEGER PRIMARY KEY,
                secret_name TEXT,
                secret_value TEXT
            )');
            
            // Check if users exist
            $result = $db->querySingle('SELECT COUNT(*) FROM ezuser');
            if ($result == 0) {
                // Insert sample users
                // Regular user with password
                $db->exec("INSERT INTO ezuser (login, email, password_hash, password_hash_type, role) 
                           VALUES ('homer', 'homer@springfield.local', '" . md5('donuts123') . "', 1, 'user')");
                
                // Admin user with password_hash_type=0 (LDAP/TextFile migrated user - no local password)
                // This simulates users migrated from LDAP that have password_hash_type=0
                $db->exec("INSERT INTO ezuser (login, email, password_hash, password_hash_type, role) 
                           VALUES ('admin', 'admin@springfield.local', '', 0, 'admin')");
                
                // Another admin with proper password
                $db->exec("INSERT INTO ezuser (login, email, password_hash, password_hash_type, role) 
                           VALUES ('marge', 'marge@springfield.local', '" . md5('bart_stop_it') . "', 1, 'admin')");
                           
                // Insert the flag as admin secret
                $db->exec("INSERT INTO admin_secrets (secret_name, secret_value) 
                           VALUES ('system_flag', '" . $db->escapeString($flag) . "')");
            }
            
            return $db;
        }
        
        /**
         * Vulnerable login function - mimics eZ Publish's _loginUser()
         * 
         * VULNERABILITY: This function does NOT check if $login or $password is empty
         * before querying the database. When password_hash_type=0, the password
         * comparison is skipped entirely, allowing passwordless login.
         * 
         * This mirrors the CVE where LDAP/TextFile handler users with password_hash_type=0
         * could be logged in without password verification.
         */
        function _loginUser($db, $login, $password) {
            // VULNERABLE: No check for empty login or password
            // The fix would add: if (empty($login) || empty($password)) return false;
            
            // Query user from database
            $stmt = $db->prepare('SELECT * FROM ezuser WHERE login = :login AND is_enabled = 1');
            $stmt->bindValue(':login', $login, SQLITE3_TEXT);
            $result = $stmt->execute();
            $user = $result->fetchArray(SQLITE3_ASSOC);
            
            if (!$user) {
                return false;
            }
            
            // VULNERABLE: When password_hash_type is 0 (LDAP/TextFile mode),
            // skip password verification entirely - this is the core vulnerability
            if ($user['password_hash_type'] == 0) {
                // User has no local password (LDAP/TextFile user)
                // In vulnerable version: authentication succeeds without password check
                return $user;
            }
            
            // For users with password_hash_type > 0, verify password
            $password_hash = md5($password);
            if ($user['password_hash'] === $password_hash) {
                return $user;
            }
            
            return false;
        }
        
        // Handle login
        if (isset($_POST['login'])) {
            $db = initDatabase($db_file, $flag);
            
            $login = $_POST['login'];
            $password = isset($_POST['password']) ? $_POST['password'] : '';
            
            $user = _loginUser($db, $login, $password);
            
            if ($user) {
                echo '<div class="success">';
                echo '<h2>Welcome, ' . htmlspecialchars($user['login']) . '!</h2>';
                echo '<p>Role: ' . htmlspecialchars($user['role']) . '</p>';
                
                if ($user['role'] === 'admin') {
                    // Fetch admin secrets
                    $secrets = $db->query('SELECT * FROM admin_secrets');
                    echo '<h3>Admin Panel - System Secrets:</h3>';
                    while ($secret = $secrets->fetchArray(SQLITE3_ASSOC)) {
                        echo '<p><strong>' . htmlspecialchars($secret['secret_name']) . ':</strong> ' 
                             . htmlspecialchars($secret['secret_value']) . '</p>';
                    }
                }
                echo '</div>';
            } else {
                echo '<div class="error">';
                echo '<p>Invalid login or password.</p>';
                echo '</div>';
            }
            
            $db->close();
        }
    ?>
</body>
</html>

