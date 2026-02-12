<?php $pageTitle = 'Two-Factor Authentication'; ?>
<?php require __DIR__ . '/layout_header.php'; ?>

<div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #1a237e 0%, #283593 100%);">
    <div style="width: 100%; max-width: 400px; padding: 20px;">
        <div style="text-align: center; margin-bottom: 32px;">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="#fff">
                <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
            </svg>
            <h1 style="color: #fff; font-size: 24px; margin-top: 12px;">Two-Factor Authentication</h1>
            <p style="color: rgba(255,255,255,0.7); font-size: 14px;">Enter the code from your authenticator app</p>
        </div>

        <div class="card">
            <h2 style="text-align: center; margin-bottom: 8px;">Verification Required</h2>
            <p style="text-align: center; color: #666; font-size: 14px; margin-bottom: 24px;">
                Open your authenticator app and enter the 6-digit verification code for your <?= APP_NAME ?> account.
            </p>

            <?php if (!empty($error)): ?>
                <div class="alert alert-danger"><?= htmlspecialchars($error) ?></div>
            <?php endif; ?>

            <form method="POST" action="/2fa">
                <div class="form-group">
                    <label for="auth_code">Authentication Code</label>
                    <input type="text" id="auth_code" name="_auth_code" required
                           autocomplete="one-time-code" inputmode="numeric" pattern="[0-9]{6}"
                           maxlength="6" placeholder="000000"
                           style="text-align: center; font-size: 24px; letter-spacing: 8px;">
                </div>

                <button type="submit" class="btn btn-primary" style="width: 100%;">Verify</button>
            </form>

            <div style="margin-top: 16px; text-align: center;">
                <a href="/logout" style="color: #666; font-size: 13px; text-decoration: none;">Cancel and return to login</a>
            </div>
        </div>
    </div>
</div>

<?php require __DIR__ . '/layout_footer.php'; ?>
