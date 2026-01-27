<?php
// SecureAuth Portal - Password Reset Handler
// This endpoint processes password reset tokens
session_start();

// Read the flag from environment or file
$flag = getenv('FLAG');
if (!$flag || $flag === 'FLAG_PLACEHOLDER') {
    // Try to read from file as fallback
    if (file_exists('/FLAG.php')) {
        include('/FLAG.php');
    }
}

$token = isset($_GET['token']) ? $_GET['token'] : '';
$email = isset($_GET['email']) ? $_GET['email'] : '';

// Get the current host header (used for validation/logging)
$host = isset($_SERVER['HTTP_HOST']) ? $_SERVER['HTTP_HOST'] : 'localhost';

// Check if Host header contains suspicious characters
// These characters indicate a Host header injection attack (CVE-2012-4520 pattern)
$dangerous_chars = ['@', ';', '?', '&', '=', '+', '$', ','];
$is_poisoned = false;

foreach ($dangerous_chars as $char) {
    if (strpos($host, $char) !== false) {
        $is_poisoned = true;
        break;
    }
}

$message = "";
$message_type = "";

if (empty($token)) {
    $message = "Invalid or missing reset token.";
    $message_type = "danger";
} elseif ($is_poisoned) {
    // Host header was poisoned - this simulates the vulnerability being exploited
    // In a real attack, the user would have clicked a link with attacker's domain
    // Here we reveal the flag to demonstrate successful exploitation
    $message = "Security Alert: Suspicious request detected!";
    $message_type = "warning";
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SecureAuth Portal - Reset Password</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <?php include("include/navigation-bar.php"); ?>

    <header class="py-5 bg-primary text-white mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Reset Password</h1>
                <p class="lead mb-0">Complete your password reset</p>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <?php if ($is_poisoned): ?>
                <!-- Security Alert - Host Header Poisoning Detected -->
                <div class="card border-danger">
                    <div class="card-header bg-danger text-white">
                        <h4 class="mb-0">⚠️ Security Incident Detected</h4>
                    </div>
                    <div class="card-body">
                        <p class="text-danger"><strong>Warning:</strong> A Host header injection attack was detected on this request.</p>
                        
                        <div class="alert alert-dark">
                            <h5>Attack Details:</h5>
                            <p><strong>Malicious Host Header:</strong></p>
                            <code class="d-block bg-light p-2 mb-2"><?= htmlspecialchars($host); ?></code>
                            <p class="mb-0">This type of attack (similar to CVE-2012-4520) allows attackers to poison password reset emails with malicious URLs.</p>
                        </div>
                        
                        <div class="alert alert-success mt-3">
                            <h5>🎯 Vulnerability Confirmed!</h5>
                            <p>You have successfully demonstrated the Host Header Injection vulnerability.</p>
                            <p><strong>Flag:</strong> <code><?= htmlspecialchars($flag); ?></code></p>
                        </div>
                        
                        <div class="mt-3">
                            <a href="index.php" class="btn btn-primary">Return to Home</a>
                        </div>
                    </div>
                </div>
                <?php else: ?>
                <!-- Normal Password Reset Form -->
                <div class="card">
                    <div class="card-header">
                        <h4>Set New Password</h4>
                    </div>
                    <div class="card-body">
                        <?php if (!empty($message)): ?>
                            <div class="alert alert-<?= $message_type; ?>" role="alert">
                                <?= $message; ?>
                            </div>
                        <?php endif; ?>
                        
                        <?php if (!empty($token)): ?>
                            <p class="text-muted">Enter your new password below.</p>
                            
                            <form method="POST" action="">
                                <input type="hidden" name="token" value="<?= htmlspecialchars($token); ?>">
                                <input type="hidden" name="email" value="<?= htmlspecialchars($email); ?>">
                                
                                <div class="mb-3">
                                    <label for="password" class="form-label">New Password</label>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                </div>
                                <div class="mb-3">
                                    <label for="confirm_password" class="form-label">Confirm Password</label>
                                    <input type="password" class="form-control" id="confirm_password" name="confirm_password" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Reset Password</button>
                            </form>
                        <?php else: ?>
                            <p>Please use the link from your password reset email.</p>
                            <a href="forgot-password.php" class="btn btn-primary">Request Password Reset</a>
                        <?php endif; ?>
                    </div>
                </div>
                <?php endif; ?>
                
                <!-- Debug Info (visible in development) -->
                <div class="card mt-4">
                    <div class="card-header">
                        <small>Request Information</small>
                    </div>
                    <div class="card-body">
                        <small class="text-muted">
                            <strong>Host:</strong> <?= htmlspecialchars($host); ?><br>
                            <strong>Token:</strong> <?= !empty($token) ? substr(htmlspecialchars($token), 0, 16) . '...' : 'None'; ?><br>
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
