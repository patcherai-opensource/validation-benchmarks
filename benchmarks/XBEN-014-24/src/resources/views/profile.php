<?php $pageTitle = 'Profile'; require __DIR__ . '/layout.php'; ?>

<nav class="navbar">
    <a href="/" class="navbar-brand">Task<span>Flow</span></a>
    <ul class="navbar-nav">
        <li><a href="/">Dashboard</a></li>
        <li><a href="/tasks">Tasks</a></li>
        <li><a href="/profile" class="active">Profile</a></li>
    </ul>
    <div class="navbar-user">
        <div class="avatar"><?php echo strtoupper(substr($user['name'], 0, 1)); ?></div>
        <span><?php echo htmlspecialchars($user['name']); ?></span>
        <a href="/logout" class="btn btn-sm btn-secondary">Logout</a>
    </div>
</nav>

<div class="container" style="max-width: 600px;">
    <h1 style="font-size: 1.5rem; color: #1a1a2e; margin-bottom: 1.5rem;">Profile</h1>

    <div class="card">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
            <div class="avatar" style="width: 64px; height: 64px; font-size: 1.5rem;"><?php echo strtoupper(substr($user['name'], 0, 1)); ?></div>
            <div>
                <h2 style="font-size: 1.2rem; margin-bottom: 0.25rem;"><?php echo htmlspecialchars($user['name']); ?></h2>
                <p style="color: #888; font-size: 0.85rem;"><?php echo htmlspecialchars($user['email']); ?></p>
            </div>
        </div>

        <table style="width: 100%;">
            <tr><td style="color: #888; width: 120px;">Name</td><td><?php echo htmlspecialchars($user['name']); ?></td></tr>
            <tr><td style="color: #888;">Email</td><td><?php echo htmlspecialchars($user['email']); ?></td></tr>
            <tr><td style="color: #888;">Role</td><td><span class="badge badge-progress"><?php echo ucfirst($user['role']); ?></span></td></tr>
        </table>
    </div>
</div>

<div class="footer">
    <p>&copy; 2024 TaskFlow. All rights reserved. | Version 5.6.28</p>
</div>

</body>
</html>