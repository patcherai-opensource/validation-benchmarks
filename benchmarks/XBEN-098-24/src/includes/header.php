<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo isset($page_title) ? htmlspecialchars($page_title) . ' · ' : ''; ?>Reposilite</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">Reposilite</a>
            <span class="version">3.5.10</span>
        </div>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/releases">Releases</a>
            <a href="/snapshots">Snapshots</a>
            <a href="/login">Login</a>
        </div>
    </nav>
    <div class="container">
