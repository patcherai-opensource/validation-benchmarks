<?php $pageTitle = 'Sign In'; ?>
<?php require __DIR__ . '/layout_header.php'; ?>

<div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #1a237e 0%, #283593 100%);">
    <div style="width: 100%; max-width: 400px; padding: 20px;">
        <div style="text-align: center; margin-bottom: 32px;">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="#fff">
                <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 6c1.4 0 2.8 1.1 2.8 2.5V11c.6 0 1.2.6 1.2 1.3v3.5c0 .6-.6 1.2-1.3 1.2H9.2c-.6 0-1.2-.6-1.2-1.3v-3.5c0-.6.6-1.2 1.3-1.2V9.5C9.2 8.1 10.6 7 12 7zm0 1.2c-.8 0-1.5.7-1.5 1.3V11h3V9.5c0-.6-.7-1.3-1.5-1.3z"/>
            </svg>
            <h1 style="color: #fff; font-size: 24px; margin-top: 12px;"><?= APP_NAME ?></h1>
            <p style="color: rgba(255,255,255,0.7); font-size: 14px;">Enterprise Security Dashboard</p>
        </div>

        <div class="card">
            <h2 style="text-align: center; margin-bottom: 24px;">Sign in to your account</h2>

            <?php if (!empty($error)): ?>
                <div class="alert alert-danger"><?= htmlspecialchars($error) ?></div>
            <?php endif; ?>

            <form method="POST" action="/login">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required autocomplete="username"
                           value="<?= htmlspecialchars($_POST['username'] ?? '') ?>">
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required autocomplete="current-password">
                </div>

                <div class="form-group">
                    <div class="checkbox-group">
                        <input type="checkbox" id="remember_me" name="_remember_me" value="1">
                        <label for="remember_me">Remember me on this device</label>
                    </div>
                </div>

                <button type="submit" class="btn btn-primary" style="width: 100%;">Sign In</button>
            </form>
        </div>

        <p style="text-align: center; color: rgba(255,255,255,0.5); font-size: 12px; margin-top: 16px;">
            Protected by two-factor authentication
        </p>
    </div>
</div>

<?php require __DIR__ . '/layout_footer.php'; ?>
