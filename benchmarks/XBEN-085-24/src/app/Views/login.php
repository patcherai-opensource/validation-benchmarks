<?php $pageTitle = 'Login - Asset Management System'; ?>
<?php include __DIR__ . '/layouts/header.php'; ?>

<div class="login-container">
    <h2>Operator Login</h2>
    <?php if (!empty($error)): ?>
        <div class="alert alert-danger"><?= htmlspecialchars($error) ?></div>
    <?php endif; ?>
    <form action="/login" method="POST" class="login-form">
        <div class="form-group">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" required autocomplete="username">
        </div>
        <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" name="password" required autocomplete="current-password">
        </div>
        <button type="submit" class="btn btn-primary">Sign In</button>
    </form>
    <p class="login-note">Access restricted to authorized personnel only.</p>
</div>

<?php include __DIR__ . '/layouts/footer.php'; ?>
