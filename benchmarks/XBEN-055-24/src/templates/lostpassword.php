<?php include __DIR__ . '/_header.php'; ?>
<div class="security-page">
    <div class="brand-header">
        <h1>Corporate Portal</h1>
        <p class="tagline">Internal Management System</p>
    </div>
    <div class="security-form-container">
        <h2>Lost Password</h2>
        <p>Enter your email address and we will send you a link with which you can reset your password.</p>
        <?php if (!empty($message)): ?>
            <div class="message message-<?= htmlspecialchars($messageType) ?>"><?= htmlspecialchars($message) ?></div>
        <?php endif; ?>
        <form id="MemberLoginForm_LostPasswordForm" action="/Account/recover" method="post" class="security-form">
            <div class="field">
                <label for="Email">Email</label>
                <input type="text" name="Email" id="Email" class="text" autocomplete="email" placeholder="your.name@portal.corp">
            </div>
            <div class="actions">
                <button type="submit" class="action" name="action_forgotPassword">Send me the password reset link</button>
            </div>
            <p><a href="/Account/signin">&larr; Back to login</a></p>
        </form>
    </div>
</div>
<?php include __DIR__ . '/_footer.php'; ?>
