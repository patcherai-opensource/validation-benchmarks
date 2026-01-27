<?php
session_start();

// Redirect if already logged in
if (isset($_SESSION['user_id'])) {
    header("Location: index.php");
    exit;
}

$message = '';
$messageType = '';

$conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'libraryDB');

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = trim($_POST['username']);
    $email = trim($_POST['email']);
    $password = $_POST['password'];
    
    // Check if username already exists
    $stmt = $conn->prepare("SELECT id FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($result->num_rows > 0) {
        $message = 'Username already taken.';
        $messageType = 'error';
    } else {
        // VULNERABILITY: No password policy enforcement during registration
        // Weak passwords are allowed (CVE-2023-2106 style vulnerability)
        // In a secure application, we would check:
        // - Minimum length (e.g., 8+ characters)
        // - Uppercase letters
        // - Lowercase letters
        // - Numbers
        // - Special characters
        
        // Only check that password is not empty
        if (strlen($password) < 1) {
            $message = 'Password cannot be empty.';
            $messageType = 'error';
        } else {
            // Hash the password (even weak ones)
            $hashed_password = password_hash($password, PASSWORD_DEFAULT);
            
            // Insert new user
            $stmt = $conn->prepare("INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, 0)");
            $stmt->bind_param("sss", $username, $email, $hashed_password);
            
            if ($stmt->execute()) {
                $message = 'Registration successful! You can now login.';
                $messageType = 'success';
            } else {
                $message = 'Registration failed. Please try again.';
                $messageType = 'error';
            }
        }
    }
    $stmt->close();
}
$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register - Calibre-Web</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>📚 Create Account</h1>
    <p class="subtitle">Join our digital library</p>
    
    <?php if ($message !== ''): ?>
        <p class="<?php echo $messageType; ?>"><?php echo htmlspecialchars($message); ?></p>
    <?php endif; ?>
    
    <form action="register.php" method="POST" class="auth-form">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required minlength="3" maxlength="50">
        
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" required>
        
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
        
        <button type="submit">Register</button>
    </form>
    
    <p class="auth-link">Already have an account? <a href="login.php">Login here</a></p>
    <p class="auth-link"><a href="index.php">← Back to Library</a></p>
</div>
<footer>
    <p>Calibre-Web v0.6.19</p>
</footer>
</body>
</html>
