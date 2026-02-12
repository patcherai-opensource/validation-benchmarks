<?php $pageTitle = 'Sign In'; require __DIR__ . '/layout.php'; ?>

<nav class="navbar">
    <a href="/" class="navbar-brand">Task<span>Flow</span></a>
    <ul class="navbar-nav">
        <li><a href="/">Dashboard</a></li>
    </ul>
    <div class="navbar-user">
        <a href="/login" class="btn btn-sm btn-primary">Sign In</a>
    </div>
</nav>

<div class="container" style="max-width: 420px; margin-top: 4rem;">
    <div class="card" style="padding: 2rem;">
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h1 style="font-size: 1.3rem; color: #1a1a2e;">Sign in to TaskFlow</h1>
            <p style="color: #888; font-size: 0.85rem; margin-top: 0.5rem;">Enter your credentials to access your workspace</p>
        </div>

        <?php if (!empty($error)): ?>
        <div class="alert alert-danger"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>

        <form method="POST" action="/login">
            <input type="hidden" name="_token" value="<?php echo htmlspecialchars($csrfToken); ?>">

            <div class="form-group">
                <label for="email">Email address</label>
                <input type="email" id="email" name="email" class="form-control" placeholder="you@company.com" required>
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" class="form-control" placeholder="Enter your password" required>
            </div>

            <button type="submit" class="btn btn-primary" style="width: 100%; justify-content: center; margin-top: 0.5rem;">
                Sign In
            </button>
        </form>

        <div style="text-align: center; margin-top: 1rem;">
            <a href="#" style="font-size: 0.8rem; color: #888; text-decoration: none;">Forgot your password?</a>
        </div>
    </div>
</div>

<div class="footer">
    <p>&copy; 2024 TaskFlow. All rights reserved. | Version 5.6.28</p>
</div>

</body>
</html>