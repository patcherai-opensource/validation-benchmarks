<?php
/**
 * Admin Dashboard
 *
 * @package   myKnowledgeBase
 */
?>

<div class="admin-header">
    <h1>Dashboard</h1>
</div>

<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value"><?php echo count($mkb_topics); ?></div>
        <div class="stat-label">Topics</div>
    </div>
    <div class="stat-card">
        <div class="stat-value"><?php echo count($mkb_faqs); ?></div>
        <div class="stat-label">FAQ Entries</div>
    </div>
    <div class="stat-card">
        <div class="stat-value"><?php echo array_sum(array_column($mkb_faqs, 'visits')); ?></div>
        <div class="stat-label">Total Views</div>
    </div>
    <div class="stat-card">
        <div class="stat-value"><?php echo count($mkb_languages); ?></div>
        <div class="stat-label">Languages</div>
    </div>
</div>

<div class="card">
    <h2>Recent Activity</h2>
    <table class="table">
        <thead>
            <tr>
                <th>Action</th>
                <th>Details</th>
                <th>User</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>FAQ Updated</td>
                <td>How do I set up myKnowledgeBase?</td>
                <td>admin</td>
                <td>2024-01-15 14:23</td>
            </tr>
            <tr>
                <td>Topic Created</td>
                <td>Troubleshooting</td>
                <td>admin</td>
                <td>2024-01-14 09:45</td>
            </tr>
            <tr>
                <td>FAQ Created</td>
                <td>File uploads are not working</td>
                <td>admin</td>
                <td>2024-01-13 16:12</td>
            </tr>
            <tr>
                <td>Configuration</td>
                <td>Updated max attachment size</td>
                <td>admin</td>
                <td>2024-01-12 11:30</td>
            </tr>
        </tbody>
    </table>
</div>

<div class="card">
    <h2>System Status</h2>
    <p>PHP Version: <?php echo PHP_VERSION; ?></p>
    <p>myKnowledgeBase Version: <?php echo htmlspecialchars($mkb_config['main.currentVersion']); ?></p>
    <p>Images Directory: <?php echo is_writable(MKB_IMAGES_DIR) ? '<span style="color:green">Writable</span>' : '<span style="color:red">Not Writable</span>'; ?></p>
</div>
