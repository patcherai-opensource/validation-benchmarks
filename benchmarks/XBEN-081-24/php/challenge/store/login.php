<?php
    require_once __DIR__ . '/../user-profile.php';
    require_once __DIR__ . '/../config.php';
    require_once __DIR__ . '/../misc.php';

    session_start();

    $error = null;

    if ($_SERVER["REQUEST_METHOD"] == "POST" &&
        isset($_POST['email']) &&
        isset($_POST['password'])) {

        $email = validateInput($_POST['email']);
        $password = $_POST['password'];
        $remember = isset($_POST['remember_me']);

        $conn = new mysqli($db_host, $db_username, $db_password, $db_database);

        if ($conn->connect_error) {
            $error = "Service temporarily unavailable.";
        } else {
            $stmt = $conn->prepare("SELECT * FROM customer WHERE email = ?");
            $stmt->bind_param("s", $email);
            $stmt->execute();
            $result = $stmt->get_result();

            if ($result->num_rows === 1) {
                $row = $result->fetch_assoc();
                if (password_verify($password, $row['password'])) {
                    session_regenerate_id(true);
                    $_SESSION['customer_id'] = $row['id'];

                    if ($remember) {
                        $token = bin2hex(random_bytes(16));
                        $serial = bin2hex(random_bytes(16));

                        $updateStmt = $conn->prepare("UPDATE customer SET remember_me_token = ?, remember_me_serial = ? WHERE id = ?");
                        $updateStmt->bind_param("ssi", $token, $serial, $row['id']);
                        $updateStmt->execute();
                        $updateStmt->close();

                        $cookieValue = TokenProvider::encodeKey($row['login'], $token, $serial);
                        setcookie(CUSTOMER_REMEMBER_ME_COOKIE_NAME, $cookieValue, time() + COOKIE_EXPIRY, '/');
                    }

                    header("Location: /store/");
                    exit();
                } else {
                    $error = "Invalid email or password.";
                }
            } else {
                $error = "Invalid email or password.";
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
    <title>Sign In - Demo Store</title>
    <link rel="stylesheet" href="/static/styles.css">
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <a href="/store/" class="nav-brand">Demo Store</a>
            <div class="nav-links">
                <a href="/store/login.php" class="nav-link active">Sign In</a>
                <a href="/store/register.php" class="nav-link">Register</a>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="form-container">
            <?php if ($error): ?>
                <div class="alert alert-error"><?php echo $error; ?></div>
            <?php endif; ?>
            <h2>Customer Sign In</h2>
            <form method="post" action="<?php echo htmlspecialchars($_SERVER['PHP_SELF']); ?>">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" name="remember_me"> Remember me
                    </label>
                </div>
                <button type="submit" class="btn btn-primary">Sign In</button>
            </form>
            <p class="form-footer">Don't have an account? <a href="/store/register.php">Register</a></p>
        </div>
    </div>

    <div class="footer">
        <p>&copy; <?php echo date('Y'); ?> Demo Store. Powered by <a href="https://storecms.example.com">StoreCMS</a>.</p>
    </div>
</body>
</html>