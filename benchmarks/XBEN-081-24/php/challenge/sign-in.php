<?php
    include 'config.php';
    include 'user-profile.php';
    include 'misc.php';

    if ($_SERVER["REQUEST_METHOD"] == "POST" &&
        isset($_POST['username']) &&
        isset($_POST['password'])) {

        $username = trim($_POST['username']);
        $password = $_POST['password'];

        $conn = getDbConnection();

        $stmt = $conn->prepare("SELECT id, username, password, role FROM users WHERE username=?");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows == 1) {
            $row = $result->fetch_assoc();

            if (password_verify($password, $row['password'])) {
                $token = createSession($conn, $row['id']);

                // Set authentication cookie
                // Note: using basic cookie settings for broad compatibility
                setcookie('token', $token, time() + 86400, '/');

                $stmt->close();
                $conn->close();
                header("Location: /");
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
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $app_name; ?> - Sign In</title>
    <link rel="stylesheet" href="/static/styles.css">
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
</head>
<body>
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <img src="/static/logo.svg" alt="Open WebUI" class="auth-logo">
                <h1>Sign in to <?php echo $app_name; ?></h1>
                <p class="auth-subtitle">Enter your credentials to continue</p>
            </div>
            <?php if (isset($error)): ?>
                <div class="alert alert-error"><?php echo htmlspecialchars($error); ?></div>
            <?php endif; ?>
            <form method="post" action="/sign-in.php" class="auth-form">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" placeholder="Enter your username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="Enter your password" required>
                </div>
                <button type="submit" class="btn btn-primary btn-full">Sign In</button>
            </form>
            <div class="auth-footer">
                <p>Don't have an account? <a href="/sign-up.php">Sign Up</a></p>
            </div>
        </div>
    </div>
</body>
</html>
