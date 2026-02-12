<?php $pageTitle = 'Log in'; include __DIR__ . '/header.php'; ?>
<div class="security-form-container">
    <div class="security-form-header">
        <h2>Log in</h2>
    </div>
    <div class="security-form-body">
        <?php if (!empty($error)): ?>
            <div class="alert alert-error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        <form method="POST" action="/Security/login">
            <div class="form-group">
                <label for="MemberLoginForm_Email">Email address</label>
                <input type="email" id="MemberLoginForm_Email" name="Email" required
                       value="<?php echo isset($_POST['Email']) ? htmlspecialchars($_POST['Email']) : ''; ?>">
            </div>
            <div class="form-group">
                <label for="MemberLoginForm_Password">Password</label>
                <input type="password" id="MemberLoginForm_Password" name="Password" required>
            </div>
            <input type="hidden" name="BackURL" value="<?php echo htmlspecialchars($backURL); ?>">
            <button type="submit" class="btn">Log in</button>
            <div class="form-links">
                <a href="/Security/lostpassword">I've lost my password</a>
            </div>
        </form>
    </div>
</div>
<?php include __DIR__ . '/footer.php'; ?>