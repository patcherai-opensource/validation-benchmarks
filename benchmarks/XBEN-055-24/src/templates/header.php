<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo isset($pageTitle) ? htmlspecialchars($pageTitle) . ' - ' : ''; ?>Greenfield Corporate Portal</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
<div class="header">
    <div class="header-inner">
        <a href="/" class="logo">Greenfield Corporate Portal</a>
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
            <?php
            require_once '/var/www/includes/database.php';
            require_once '/var/www/includes/session.php';
            $currentMember = ss_get_current_member();
            if ($currentMember): ?>
                <a href="/admin">Admin</a>
                <a href="/Security/logout">Log out (<?php echo htmlspecialchars($currentMember['FirstName']); ?>)</a>
            <?php else: ?>
                <a href="/Security/login">Log in</a>
            <?php endif; ?>
        </nav>
    </div>
</div>