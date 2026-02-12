<?php
    include 'config.php';
    include 'user-profile.php';
    include 'misc.php';

    // Check if signup is enabled
    $conn = getDbConnection();
    $stmt = $conn->prepare("SELECT setting_value FROM system_settings WHERE setting_key='allow_signup'");
    $stmt->execute();
    $result = $stmt->get_result();
    $signup_enabled = true;
    if ($result->num_rows === 1) {
        $row = $result->fetch_assoc();
        $signup_enabled = ($row['setting_value'] === 'true');
    }
    $stmt->close();

    if (!$signup_enabled) {
        $conn->close();
        http_response_code(403);
        die("Registration is currently disabled by the administrator.");
    }

    if ($_SERVER["REQUEST_METHOD"] == "POST" &&
        isset($_POST['username']) &&
        isset($_POST['password']) &&
        isset($_POST['email'])) {

        $username = trim($_POST['username']);
        $email = trim($_POST['email']);
        $password = $_POST['password'];

        if (strlen($username) < 3 || strlen($username) > 50) {
            $error = "Username must be between 3 and 50 characters.";
        } elseif (strlen($password) < 6) {
            $error = "Password must be at least 6 characters.";
        } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $error = "Please enter a valid email address.";
        } else {
            $password_hash = password_hash($password, PASSWORD_DEFAULT);

            $stmt = $conn->prepare("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, 'user')");
            $stmt->bind_param("sss", $username, $email, $password_hash);

            if ($stmt->execute()) {
                $stmt->close();
                $conn->close();
                header("Location: /sign-in.php?registered=1");
                exit();
            } else {
                $error = "Username or email already exists.";
            }

            $stmt->close();
        }
    }

    $conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $app_name; ?> - Sign Up</title>
    <link rel="stylesheet" href="/static/styles.css">
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
</head>
<body>
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <img src="/static/logo.svg" alt="Open WebUI" class="auth-logo">
                <h1>Create an Account</h1>
                <p class="auth-subtitle">Join <?php echo $app_name; ?> to get started</p>
            </div>
            <?php if (isset($error)): ?>
                <div class="alert alert-error"><?php echo htmlspecialchars($error); ?></div>
            <?php endif; ?>
            <form method="post" action="/sign-up.php" class="auth-form">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" placeholder="Choose a username" required
                           value="<?php echo isset($username) ? htmlspecialchars($username) : ''; ?>">
                </div>
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" placeholder="Enter your email" required
                           value="<?php echo isset($email) ? htmlspecialchars($email) : ''; ?>">
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="Choose a password" required>
                </div>
                <button type="submit" class="btn btn-primary btn-full">Create Account</button>
            </form>
            <div class="auth-footer">
                <p>Already have an account? <a href="/sign-in.php">Sign In</a></p>
            </div>
        </div>
    </div>
</body>
</html>
