<?php
// SecureAuth Portal - Password Reset
// VULNERABLE: Uses unsanitized Host header to generate reset URLs
session_start();

$message = "";
$message_type = "";
$reset_link = "";

// Process password reset request
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = isset($_POST["email"]) ? trim($_POST["email"]) : "";
    
    if (empty($email)) {
        $message = "Please enter your email address.";
        $message_type = "danger";
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $message = "Please enter a valid email address.";
        $message_type = "danger";
    } else {
        // Generate reset token
        $token = bin2hex(random_bytes(32));
        
        // VULNERABILITY: Using raw Host header without validation
        // This mimics CVE-2012-4520 in Django
        $host = isset($_SERVER['HTTP_HOST']) ? $_SERVER['HTTP_HOST'] : 'localhost';
        
        // Build the reset URL using the unsanitized host
        $protocol = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
        $reset_link = $protocol . "://" . $host . "/reset.php?token=" . $token . "&email=" . urlencode($email);
        
        // In a real application, this would send an email
        // For this demo, we show what the email would contain
        $message = "Password reset instructions have been sent to: " . htmlspecialchars($email);
        $message_type = "success";
        
        // Store the generated link for display (simulating email preview)
        $_SESSION['reset_preview'] = $reset_link;
        $_SESSION['reset_email'] = $email;
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SecureAuth Portal - Forgot Password</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <?php include("include/navigation-bar.php"); ?>

    <header class="py-5 bg-primary text-white mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Password Recovery</h1>
                <p class="lead mb-0">Reset your SecureAuth account password</p>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h4>Forgot Your Password?</h4>
                    </div>
                    <div class="card-body">
                        <?php if (!empty($message)): ?>
                            <div class="alert alert-<?= $message_type; ?>" role="alert">
                                <?= $message; ?>
                            </div>
                        <?php endif; ?>
                        
                        <p class="text-muted">Enter your email address and we'll send you a link to reset your password.</p>
                        
                        <form method="POST" action="">
                            <div class="mb-3">
                                <label for="email" class="form-label">Email Address</label>
                                <input type="email" class="form-control" id="email" name="email" 
                                       placeholder="user@company.com" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Send Reset Link</button>
                        </form>
                        
                        <hr>
                        <p class="text-center mb-0">
                            <a href="login.php">Back to Login</a>
                        </p>
                    </div>
                </div>
                
                <?php if (isset($_SESSION['reset_preview'])): ?>
                <!-- Email Preview Section (for demonstration) -->
                <div class="card mt-4">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0">📧 Email Preview (Debug Mode)</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>To:</strong> <?= htmlspecialchars($_SESSION['reset_email']); ?></p>
                        <p><strong>Subject:</strong> SecureAuth Password Reset Request</p>
                        <hr>
                        <p>Hello,</p>
                        <p>We received a request to reset your password. Click the link below to proceed:</p>
                        <p class="bg-light p-2 border rounded" style="word-break: break-all;">
                            <a href="<?= htmlspecialchars($_SESSION['reset_preview']); ?>">
                                <?= htmlspecialchars($_SESSION['reset_preview']); ?>
                            </a>
                        </p>
                        <p class="text-muted small">This link will expire in 24 hours.</p>
                    </div>
                </div>
                <?php 
                    // Clear session after display
                    unset($_SESSION['reset_preview']);
                    unset($_SESSION['reset_email']);
                endif; 
                ?>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
