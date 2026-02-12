<?php
    require_once __DIR__ . '/../user-profile.php';
    require_once __DIR__ . '/../config.php';
    require_once __DIR__ . '/../misc.php';

    session_start();

    // If already authenticated, redirect to dashboard
    if (isset($_SESSION['admin_id'])) {
        header("Location: /admin/");
        exit();
    }

    $error = null;

    if ($_SERVER["REQUEST_METHOD"] == "POST" &&
        isset($_POST['username']) &&
        isset($_POST['password'])) {

        $username = validateInput($_POST['username']);
        $password = $_POST['password'];
        $remember = isset($_POST['remember_me']);

        $conn = new mysqli($db_host, $db_username, $db_password, $db_database);

        if ($conn->connect_error) {
            $error = "Service temporarily unavailable.";
        } else {
            $stmt = $conn->prepare("SELECT * FROM admin WHERE login = ?");
            $stmt->bind_param("s", $username);
            $stmt->execute();
            $result = $stmt->get_result();

            if ($result->num_rows === 1) {
                $row = $result->fetch_assoc();
                if (password_verify($password, $row['password'])) {
                    session_regenerate_id(true);
                    $_SESSION['admin_id'] = $row['id'];
                    $_SESSION['admin_login'] = $row['login'];

                    if ($remember) {
                        $token = bin2hex(random_bytes(16));
                        $serial = bin2hex(random_bytes(16));

                        $updateStmt = $conn->prepare("UPDATE admin SET remember_me_token = ?, remember_me_serial = ? WHERE id = ?");
                        $updateStmt->bind_param("ssi", $token, $serial, $row['id']);
                        $updateStmt->execute();
                        $updateStmt->close();

                        $cookieValue = TokenProvider::encodeKey($row['login'], $token, $serial);
                        setcookie(ADMIN_REMEMBER_ME_COOKIE_NAME, $cookieValue, time() + COOKIE_EXPIRY, '/admin');
                    }

                    header("Location: /admin/");
                    exit();
                } else {
                    $error = "Invalid credentials.";
                }
            } else {
                $error = "Invalid credentials.";
            }
            $stmt->close();
            $conn->close();
        }
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Administration</title>
    <link rel="stylesheet" href="/static/styles.css">
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
</head>
<body class="admin-body">
    <div class="admin-login-container">
        <div class="admin-login-box">
            <h1>Administration</h1>
            <p class="version-info">Version 2.1.2</p>
            <?php if ($error): ?>
                <div class="alert alert-error"><?php echo $error; ?></div>
            <?php endif; ?>
            <form method="post" action="<?php echo htmlspecialchars($_SERVER['PHP_SELF']); ?>">
                <div class="form-group">
                    <label for="username">Admin Username</label>
                    <input type="text" id="username" name="username" required autocomplete="username">
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required autocomplete="current-password">
                </div>
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" name="remember_me"> Remember me on this computer
                    </label>
                </div>
                <button type="submit" class="btn btn-admin">Sign In</button>
            </form>
        </div>
    </div>
</body>
</html>