<?php $pageTitle = 'Lost Password'; include __DIR__ . '/header.php'; ?>
<div class="security-form-container">
    <div class="security-form-header">
        <h2>I've lost my password</h2>
    </div>
    <div class="security-form-body">
        <?php if (!empty($message)): ?>
            <div class="alert alert-info"><?php echo htmlspecialchars($message); ?></div>
        <?php endif; ?>
        <?php if (!empty($error)): ?>
            <div class="alert alert-error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        <p style="margin-bottom: 16px; font-size: 0.9rem; color: #666;">Enter your email address and we'll send you a link to reset your password.</p>
        <form method="POST" action="/Security/lostpassword">
            <div class="form-group">
                <label for="ForgotPasswordForm_Email">Email address</label>
                <input type="email" id="ForgotPasswordForm_Email" name="Email" required>
            </div>
            <button type="submit" class="btn">Send me the password reset link</button>
            <div class="form-links">
                <a href="/Security/login">Back to login</a>
            </div>
        </form>
    </div>
</div>
<?php include __DIR__ . '/footer.php'; ?>