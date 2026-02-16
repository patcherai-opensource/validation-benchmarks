<?php include __DIR__ . '/_header.php'; ?>
<div class="security-page">
    <div class="brand-header">
        <h1>Corporate Portal</h1>
        <p class="tagline">Internal Management System</p>
    </div>
    <div class="security-form-container">
        <h2>Log in</h2>
        <?php if (!empty($message)): ?>
            <div class="message message-<?= htmlspecialchars($messageType) ?>"><?= htmlspecialchars($message) ?></div>
        <?php endif; ?>
        <form id="MemberLoginForm_LoginForm" action="/Account/signin" method="post" class="security-form">
            <input type="hidden" name="AuthenticationMethod" value="MemberAuthenticator">
            <?php if (!empty($backURL)): ?>
                <input type="hidden" name="BackURL" value="<?= htmlspecialchars($backURL) ?>">
            <?php endif; ?>
            <div class="field">
                <label for="Email">Email</label>
                <input type="text" name="Email" id="Email" class="text" autocomplete="email">
            </div>
            <div class="field">
                <label for="Password">Password</label>
                <input type="password" name="Password" id="Password" class="text">
            </div>
            <div class="actions">
                <button type="submit" class="action" name="action_dologin">Log in</button>
            </div>
            <p id="ForgotPassword"><a href="/Account/recover">I've lost my password</a></p>
        </form>
    </div>
</div>
<?php include __DIR__ . '/_footer.php'; ?>
