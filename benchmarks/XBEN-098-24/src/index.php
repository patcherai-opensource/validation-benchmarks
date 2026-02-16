<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reposilite - Repository Manager</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="header-bar">
        <div class="header-inner">
            <a href="/" class="header-brand">Reposilite</a>
            <nav class="header-nav">
                <a href="/browse">Browse</a>
                <a href="/dashboard">Dashboard</a>
            </nav>
        </div>
    </div>
    <div class="main-content">
        <div class="hero">
            <h1>Reposilite</h1>
            <p class="subtitle">Lightweight and easy-to-use repository manager for Maven artifacts</p>
        </div>
        <div class="card-grid">
            <div class="card">
                <h3>Repositories</h3>
                <ul class="repo-list">
                    <li><a href="/browse/releases">releases</a> <span class="badge">public</span></li>
                    <li><a href="/browse/snapshots">snapshots</a> <span class="badge">public</span></li>
                    <li><a href="/browse/public">public</a> <span class="badge">public</span></li>
                </ul>
            </div>
            <div class="card">
                <h3>Quick Links</h3>
                <ul class="repo-list">
                    <li><a href="/api/status/instance">Instance Status</a></li>
                    <li><a href="/browse">Browse Artifacts</a></li>
                    <li><a href="/dashboard">Admin Dashboard</a></li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>