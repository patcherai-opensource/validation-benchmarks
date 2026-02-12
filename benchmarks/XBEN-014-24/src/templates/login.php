    <div class="container">
        <div class="card" style="max-width: 420px; margin: 60px auto;">
            <h2>Sign In</h2>
            <?php if (isset($login_error)): ?>
                <div class="alert alert-danger"><?php echo htmlspecialchars($login_error); ?></div>
            <?php endif; ?>
            <form method="POST" action="/?page=login">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" autocomplete="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" autocomplete="current-password" required>
                </div>
                <div class="form-group-inline">
                    <input type="checkbox" id="remember_me" name="remember_me" value="1">
                    <label for="remember_me">Remember me on this device</label>
                </div>
                <button type="submit" class="btn">Sign In</button>
            </form>
        </div>
    </div>