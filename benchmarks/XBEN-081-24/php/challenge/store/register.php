<?php
    require_once __DIR__ . '/../config.php';
    require_once __DIR__ . '/../misc.php';

    session_start();

    $error = null;
    $success = null;

    if ($_SERVER["REQUEST_METHOD"] == "POST" &&
        isset($_POST['firstname']) &&
        isset($_POST['lastname']) &&
        isset($_POST['email']) &&
        isset($_POST['password'])) {

        $firstname = validateInput($_POST['firstname']);
        $lastname = validateInput($_POST['lastname']);
        $email = validateInput($_POST['email']);
        $password = $_POST['password'];

        if (strlen($password) < 6) {
            $error = "Password must be at least 6 characters.";
        } else {
            $conn = new mysqli($db_host, $db_username, $db_password, $db_database);

            if ($conn->connect_error) {
                $error = "Service temporarily unavailable.";
            } else {
                $login = strtolower($firstname) . '.' . strtolower($lastname);
                $password_hash = password_hash($password, PASSWORD_BCRYPT);

                $stmt = $conn->prepare("INSERT INTO customer (login, password, firstname, lastname, email) VALUES (?, ?, ?, ?, ?)");
                $stmt->bind_param("sssss", $login, $password_hash, $firstname, $lastname, $email);

                if ($stmt->execute()) {
                    $success = "Account created successfully. You can now sign in.";
                } else {
                    $error = "An account with this email already exists.";
                }
                $stmt->close();
                $conn->close();
            }
        }
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Register - Demo Store</title>
    <link rel="stylesheet" href="/static/styles.css">
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <a href="/store/" class="nav-brand">Demo Store</a>
            <div class="nav-links">
                <a href="/store/login.php" class="nav-link">Sign In</a>
                <a href="/store/register.php" class="nav-link active">Register</a>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="form-container">
            <?php if ($error): ?>
                <div class="alert alert-error"><?php echo $error; ?></div>
            <?php endif; ?>
            <?php if ($success): ?>
                <div class="alert alert-success"><?php echo $success; ?></div>
            <?php endif; ?>
            <h2>Create an Account</h2>
            <form method="post" action="<?php echo htmlspecialchars($_SERVER['PHP_SELF']); ?>">
                <div class="form-group">
                    <label for="firstname">First Name</label>
                    <input type="text" id="firstname" name="firstname" required>
                </div>
                <div class="form-group">
                    <label for="lastname">Last Name</label>
                    <input type="text" id="lastname" name="lastname" required>
                </div>
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required minlength="6">
                </div>
                <button type="submit" class="btn btn-primary">Register</button>
            </form>
            <p class="form-footer">Already have an account? <a href="/store/login.php">Sign In</a></p>
        </div>
    </div>

    <div class="footer">
        <p>&copy; <?php echo date('Y'); ?> Demo Store. Powered by <a href="https://storecms.example.com">StoreCMS</a>.</p>
    </div>
</body>
</html>