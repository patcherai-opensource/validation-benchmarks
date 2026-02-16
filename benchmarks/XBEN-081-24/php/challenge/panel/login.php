<?php
    include '../config.php';
    include '../misc.php';

    session_start();

    // Check for admin persistence cookie (remember-me)
    if (!isset($_SESSION['admin_id']) && isset($_COOKIE[$admin_persist_cookie])) {
        $admin = restoreAdminSession($_COOKIE[$admin_persist_cookie]);
        if ($admin !== null) {
            $_SESSION['admin_id'] = $admin['id'];
            $_SESSION['admin_login'] = $admin['login'];
            $_SESSION['admin_name'] = $admin['firstname'] . ' ' . $admin['lastname'];
            header("Location: index.php");
            exit();
        }
    }

    if (isset($_SESSION['admin_id'])) {
        header("Location: index.php");
        exit();
    }

    if ($_SERVER["REQUEST_METHOD"] == "POST" &&
        isset($_POST['username']) &&
        isset($_POST['password'])) {

        $username = validateInput($_POST['username']);
        $password = $_POST['password'];

        $pdo = getDbConnection();

        $stmt = $pdo->prepare("SELECT id, login, password, firstname, lastname FROM admin_users WHERE login = ?");
        $stmt->execute([$username]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($row) {

            if (password_verify($password, $row['password'])) {
                session_regenerate_id();
                $_SESSION['admin_id'] = $row['id'];
                $_SESSION['admin_login'] = $row['login'];
                $_SESSION['admin_name'] = $row['firstname'] . ' ' . $row['lastname'];

                // Set remember-me cookie if requested
                if (isset($_POST['remember_me']) && $_POST['remember_me'] == '1') {
                    setAdminPersistCookie($row['login'], $admin_persist_cookie, $persist_cookie_lifetime);
                }

                header("Location: index.php");
                exit();
            } else {
                $error = "Invalid credentials.";
            }
        } else {
            $error = "Invalid credentials.";
        }
    }
?>
<!doctype html>
<html>
    <head>
        <title>Admin Login - Velora CMS</title>
        <link rel="stylesheet" href="../static/styles.css">
        <link rel="icon" href="../static/favicon.ico" type="image/x-icon">
    </head>
    <body>
        <div class="admin-header">
            <div class="header-inner">
                <a href="login.php" class="logo">Velora Admin</a>
            </div>
        </div>

        <div class="container">
            <div class="form-box">
                <?php if (isset($error)): ?>
                    <div class="error"><?php echo $error; ?></div>
                <?php endif; ?>
                <h1>Administration Login</h1>
                <form method="post" action="login.php">
                    <table width="100%">
                        <tr>
                            <td width="120px" align="right">Username:</td>
                            <td><input type="text" name="username" required></td>
                        </tr>
                        <tr>
                            <td align="right">Password:</td>
                            <td><input type="password" name="password" required></td>
                        </tr>
                        <tr>
                            <td></td>
                            <td><label><input type="checkbox" name="remember_me" value="1"> Remember me</label></td>
                        </tr>
                        <tr>
                            <td colspan="2" align="right">
                                <input class="button" type="submit" value="Sign In">
                            </td>
                        </tr>
                    </table>
                </form>
            </div>
        </div>

        <div class="footer">
            <p>&copy; 2024 Velora CMS Administration</p>
        </div>
    </body>
</html>
