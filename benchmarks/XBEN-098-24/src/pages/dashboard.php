<?php $page_title = 'Dashboard'; include __DIR__ . '/../includes/header.php'; ?>

<h1>Repositories</h1>
<div class="card-grid">
    <div class="card">
        <h3><a href="/releases">releases</a></h3>
        <p>Release artifacts repository</p>
        <span class="badge">Maven</span>
    </div>
    <div class="card">
        <h3><a href="/snapshots">snapshots</a></h3>
        <p>Snapshot artifacts repository</p>
        <span class="badge">Maven</span>
    </div>
</div>

<h2>Statistics</h2>
<div class="stats-grid">
    <div class="stat-card">
        <span class="stat-value">247</span>
        <span class="stat-label">Total Artifacts</span>
    </div>
    <div class="stat-card">
        <span class="stat-value">1.2 GB</span>
        <span class="stat-label">Disk Usage</span>
    </div>
    <div class="stat-card">
        <span class="stat-value">15,842</span>
        <span class="stat-label">Total Downloads</span>
    </div>
    <div class="stat-card">
        <span class="stat-value">3</span>
        <span class="stat-label">Active Tokens</span>
    </div>
</div>

<?php include __DIR__ . '/../includes/footer.php'; ?>
