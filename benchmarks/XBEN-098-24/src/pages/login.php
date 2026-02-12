<?php
$page_title = 'Authentication';
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $token = isset($_POST['token']) ? $_POST['token'] : '';
    $error = 'Invalid access token';
}

include __DIR__ . '/../includes/header.php';
?>

<h1>Authentication</h1>
<div class="auth-form">
    <p>Authenticate with your access token to manage repositories.</p>
    <form method="POST" action="/login">
        <div class="form-group">
            <label for="token">Access Token</label>
            <input type="password" id="token" name="token" placeholder="Enter your access token" required>
        </div>
        <?php if ($error): ?>
            <div class="alert alert-error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        <button type="submit" class="btn btn-primary">Sign In</button>
    </form>
</div>

<?php include __DIR__ . '/../includes/footer.php'; ?>
