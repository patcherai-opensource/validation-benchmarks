<?php include __DIR__ . '/layout_header.php'; ?>
<div class="navbar">
    <div class="brand"><span>&#9670;</span> Meridian Platform</div>
</div>
<div class="container" style="max-width: 400px; margin-top: 80px;">
    <div class="card">
        <h2>Sign In</h2>
        <p style="margin-bottom: 20px;">Access the management console.</p>
        <?php if (!empty($error)): ?>
            <div class="alert alert-danger"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" autocomplete="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" autocomplete="current-password" required>
            </div>
            <button type="submit" class="btn btn-primary" style="width:100%;">Sign In</button>
        </form>
    </div>
</div>
<?php include __DIR__ . '/layout_footer.php'; ?>
