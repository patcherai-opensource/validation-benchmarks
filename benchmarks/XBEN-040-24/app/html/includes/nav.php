<nav class="main-nav">
    <div class="nav-brand">NetMon</div>
    <ul class="nav-links">
        <li><a href="index.php" class="<?php echo basename($_SERVER['PHP_SELF']) == 'index.php' ? 'active' : ''; ?>">Dashboard</a></li>
        <li><a href="devices.php" class="<?php echo basename($_SERVER['PHP_SELF']) == 'devices.php' ? 'active' : ''; ?>">Devices</a></li>
        <li><a href="ports.php" class="<?php echo basename($_SERVER['PHP_SELF']) == 'ports.php' ? 'active' : ''; ?>">Ports</a></li>
        <li class="nav-dropdown">
            <a href="#" class="<?php echo basename($_SERVER['PHP_SELF']) == 'search.php' ? 'active' : ''; ?>">Search &#9662;</a>
            <ul class="dropdown-menu">
                <li><a href="search.php?type=ipv4">IPv4 Addresses</a></li>
                <li><a href="search.php?type=hardware">Hardware Addresses</a></li>
            </ul>
        </li>
        <li><a href="alerts.php" class="<?php echo basename($_SERVER['PHP_SELF']) == 'alerts.php' ? 'active' : ''; ?>">Alerts</a></li>
        <li><a href="eventlog.php" class="<?php echo basename($_SERVER['PHP_SELF']) == 'eventlog.php' ? 'active' : ''; ?>">Event Log</a></li>
    </ul>
    <div class="nav-user">
        <span><?php echo htmlspecialchars($_SESSION['realname'] ?? $_SESSION['username'] ?? ''); ?></span>
        <a href="logout.php" class="btn-logout">Logout</a>
    </div>
</nav>
