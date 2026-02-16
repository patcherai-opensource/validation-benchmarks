<?php
/**
 * System information page - Admin
 *
 * @package   myKnowledgeBase
 */
?>

<div class="admin-header">
    <h1>System Information</h1>
</div>

<div class="card">
    <h2>Environment</h2>
    <table class="table">
        <tbody>
            <tr><td style="width:40%">myKnowledgeBase Version</td><td><?php echo htmlspecialchars($mkb_config['main.currentVersion']); ?></td></tr>
            <tr><td>PHP Version</td><td><?php echo PHP_VERSION; ?></td></tr>
            <tr><td>Web Server</td><td><?php echo htmlspecialchars($_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'); ?></td></tr>
            <tr><td>Operating System</td><td><?php echo PHP_OS; ?></td></tr>
            <tr><td>Document Root</td><td><?php echo htmlspecialchars($_SERVER['DOCUMENT_ROOT'] ?? ''); ?></td></tr>
            <tr><td>Max Upload Size</td><td><?php echo ini_get('upload_max_filesize'); ?></td></tr>
            <tr><td>Max POST Size</td><td><?php echo ini_get('post_max_size'); ?></td></tr>
            <tr><td>Memory Limit</td><td><?php echo ini_get('memory_limit'); ?></td></tr>
        </tbody>
    </table>
</div>

<div class="card">
    <h2>Directory Permissions</h2>
    <table class="table">
        <thead>
            <tr><th>Directory</th><th>Status</th></tr>
        </thead>
        <tbody>
            <tr>
                <td>/images/</td>
                <td><?php echo is_writable(MKB_IMAGES_DIR) ? '<span style="color:green">Writable</span>' : '<span style="color:red">Not Writable</span>'; ?></td>
            </tr>
            <tr>
                <td>/assets/</td>
                <td><?php echo is_readable(MKB_ROOT_DIR . '/assets/') ? '<span style="color:green">Readable</span>' : '<span style="color:red">Not Readable</span>'; ?></td>
            </tr>
        </tbody>
    </table>
</div>

<div class="card">
    <h2>PHP Extensions</h2>
    <p>
    <?php
    $required_exts = ['gd', 'json', 'mbstring', 'session', 'fileinfo'];
    foreach ($required_exts as $ext) {
        $loaded = extension_loaded($ext);
        echo '<span style="margin-right:15px;color:' . ($loaded ? 'green' : 'red') . ';">';
        echo htmlspecialchars($ext) . ': ' . ($loaded ? '✓' : '✗');
        echo '</span>';
    }
    ?>
    </p>
</div>
