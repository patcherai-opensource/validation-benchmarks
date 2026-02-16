<?php $pageTitle = 'Sign In - SecurePortal'; ?>
<?php require __DIR__ . '/layout_header.php'; ?>

<div class="auth-container">
    <div class="auth-card">
        <div class="logo">
            <h1>SecurePortal</h1>
            <p>Sign in to your account</p>
        </div>

        <?php if ($error): ?>
            <div class="alert alert-error"><?= htmlspecialchars($error) ?></div>
        <?php endif; ?>

        <form method="POST" action="/auth/signin">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" autocomplete="username" required
                       value="<?= htmlspecialchars($_POST['username'] ?? '') ?>">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" autocomplete="current-password" required>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="stay_signed_in" name="stay_signed_in" value="1">
                <label for="stay_signed_in">Stay signed in</label>
            </div>
            <button type="submit" class="btn" style="width: 100%;">Sign In</button>
        </form>
    </div>
</div>

<?php require __DIR__ . '/layout_footer.php'; ?>
