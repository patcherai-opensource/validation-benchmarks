<?php include __DIR__ . '/_header.php'; ?>
<div class="security-page">
    <div class="brand-header">
        <h1>Corporate Portal</h1>
        <p class="tagline">Internal Management System</p>
    </div>
    <div class="security-form-container">
        <h2>Change Password</h2>
        <?php if (!empty($message)): ?>
            <div class="message message-<?= htmlspecialchars($messageType) ?>"><?= htmlspecialchars($message) ?></div>
        <?php endif; ?>
        <form id="ChangePasswordForm" action="/Account/resetpassword" method="post" class="security-form">
            <input type="hidden" name="t" value="<?= $token ?>">
            <div class="field">
                <label for="NewPassword">New Password</label>
                <input type="password" name="NewPassword" id="NewPassword" class="text" required minlength="8">
            </div>
            <div class="field">
                <label for="ConfirmPassword">Confirm Password</label>
                <input type="password" name="ConfirmPassword" id="ConfirmPassword" class="text" required minlength="8">
            </div>
            <div class="actions">
                <button type="submit" class="action" name="action_changepassword">Change Password</button>
            </div>
        </form>
    </div>
</div>
<?php include __DIR__ . '/_footer.php'; ?>
