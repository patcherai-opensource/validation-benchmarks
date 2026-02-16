<nav class="sidebar">
    <div class="sidebar-brand">
        <h2>CMF</h2>
        <span>v3.3.9</span>
    </div>
    <ul class="sidebar-nav">
        <li><a href="/admin/dashboard.php" class="<?php echo basename($_SERVER['PHP_SELF']) === 'dashboard.php' ? 'active' : ''; ?>">Dashboard</a></li>
        <li><a href="/admin/customers.php" class="<?php echo basename($_SERVER['PHP_SELF']) === 'customers.php' ? 'active' : ''; ?>">Customers</a></li>
        <li><a href="/admin/segments.php" class="<?php echo basename($_SERVER['PHP_SELF']) === 'segments.php' ? 'active' : ''; ?>">Segments</a></li>
        <li><a href="/admin/activities.php" class="<?php echo basename($_SERVER['PHP_SELF']) === 'activities.php' ? 'active' : ''; ?>">Activities</a></li>
        <li><a href="/admin/settings.php" class="<?php echo basename($_SERVER['PHP_SELF']) === 'settings.php' ? 'active' : ''; ?>">Settings</a></li>
        <li class="separator"></li>
        <li><a href="/admin/logout.php">Sign Out</a></li>
    </ul>
</nav>