<?php $pageTitle = 'Verification Required - SecurePortal'; ?>
<?php require __DIR__ . '/layout_header.php'; ?>

<div class="auth-container">
    <div class="auth-card">
        <div class="logo">
            <h1>SecurePortal</h1>
            <p>Two-factor authentication</p>
        </div>

        <div class="alert alert-info">
            Enter the 6-digit code from your authenticator app to complete sign-in.
        </div>

        <?php if ($error): ?>
            <div class="alert alert-error"><?= htmlspecialchars($error) ?></div>
        <?php endif; ?>

        <form method="POST" action="/auth/verify">
            <div class="form-group">
                <label for="auth_code">Verification Code</label>
                <input type="text" id="auth_code" name="auth_code" maxlength="6"
                       pattern="[0-9]{6}" autocomplete="one-time-code"
                       placeholder="000000" required autofocus
                       style="text-align: center; font-size: 1.5rem; letter-spacing: 0.5rem;">
            </div>
            <button type="submit" class="btn" style="width: 100%;">Verify</button>
        </form>

        <p style="text-align: center; margin-top: 1.5rem;">
            <a href="/auth/signout" style="color: #888; font-size: 0.85rem; text-decoration: none;">Cancel and sign out</a>
        </p>
    </div>
</div>

<?php require __DIR__ . '/layout_footer.php'; ?>
