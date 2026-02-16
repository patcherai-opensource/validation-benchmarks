<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($title ?? 'Admin') ?> - Corporate Portal CMS</title>
    <link rel="stylesheet" href="/css/admin.css">
</head>
<body class="admin-panel">
    <nav class="cms-menu">
        <div class="cms-menu-header">
            <a href="/admin/pages" class="cms-brand">Corporate Portal</a>
        </div>
        <ul class="cms-menu-list">
            <li><a href="/admin/pages" class="cms-menu-item<?= ($title === 'Page Management') ? ' active' : '' ?>">Pages</a></li>
            <li><a href="/admin/settings" class="cms-menu-item<?= ($title === 'Settings') ? ' active' : '' ?>">Settings</a></li>
            <li><a href="/admin/security" class="cms-menu-item<?= ($title === 'Security') ? ' active' : '' ?>">Security</a></li>
        </ul>
        <div class="cms-menu-footer">
            <span class="member-info"><?= htmlspecialchars($memberName ?? '') ?></span>
            <a href="/Account/signout" class="logout-link">Log out</a>
        </div>
    </nav>
    <main class="cms-main">
