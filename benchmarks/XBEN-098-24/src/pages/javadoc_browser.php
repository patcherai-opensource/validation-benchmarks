<?php
$page_title = 'Javadoc · ' . htmlspecialchars($gav);

include __DIR__ . '/../includes/header.php';
?>

<div class="breadcrumb">
    <a href="/">repositories</a> / <a href="/<?php echo htmlspecialchars($repository); ?>"><?php echo htmlspecialchars($repository); ?></a> / <?php echo htmlspecialchars($gav); ?> / <strong>javadoc</strong>
</div>

<h1>Javadoc Browser</h1>
<p class="subtitle">Browsing expanded javadoc for <code><?php echo htmlspecialchars($gav); ?></code> in <code><?php echo htmlspecialchars($repository); ?></code></p>

<div class="file-browser">
    <table class="file-table">
        <thead>
            <tr>
                <th>Name</th>
                <th>Last Modified</th>
                <th>Size</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><span class="icon">📄</span> <a href="/javadoc/<?php echo htmlspecialchars($repository); ?>/<?php echo htmlspecialchars($gav); ?>/raw/index.html">index.html</a></td>
                <td>2024-05-28 14:30</td>
                <td>12 KB</td>
            </tr>
            <tr>
                <td><span class="icon">📁</span> <a href="/javadoc/<?php echo htmlspecialchars($repository); ?>/<?php echo htmlspecialchars($gav); ?>/raw/com/reposilite/package-summary.html">com/reposilite/package-summary.html</a></td>
                <td>2024-05-28 14:30</td>
                <td>8 KB</td>
            </tr>
            <tr>
                <td><span class="icon">📄</span> <a href="/javadoc/<?php echo htmlspecialchars($repository); ?>/<?php echo htmlspecialchars($gav); ?>/raw/stylesheet.css">stylesheet.css</a></td>
                <td>2024-05-28 14:30</td>
                <td>4 KB</td>
            </tr>
            <tr>
                <td><span class="icon">📄</span> <a href="/javadoc/<?php echo htmlspecialchars($repository); ?>/<?php echo htmlspecialchars($gav); ?>/raw/allclasses-index.html">allclasses-index.html</a></td>
                <td>2024-05-28 14:30</td>
                <td>24 KB</td>
            </tr>
            <tr>
                <td><span class="icon">📄</span> <a href="/javadoc/<?php echo htmlspecialchars($repository); ?>/<?php echo htmlspecialchars($gav); ?>/raw/overview-tree.html">overview-tree.html</a></td>
                <td>2024-05-28 14:30</td>
                <td>6 KB</td>
            </tr>
        </tbody>
    </table>
</div>

<?php include __DIR__ . '/../includes/footer.php'; ?>
