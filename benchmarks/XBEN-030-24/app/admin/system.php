<?php
/**
 * Administration - System Information
 */

gp_page_header('System Information');
?>
<div class="gp-content">
    <h2>Administration</h2>
    <?php gp_admin_tabs('system'); ?>

    <h3>System Information</h3>
    <table class="gp-table gp-detail-table">
        <tr><th>Application</th><td><?php echo APP_NAME; ?></td></tr>
        <tr><th>Version</th><td><?php echo APP_VERSION; ?></td></tr>
        <tr><th>PHP Version</th><td><?php echo PHP_VERSION; ?></td></tr>
        <tr><th>Server Software</th><td><?php echo gp_escape_html($_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'); ?></td></tr>
        <tr><th>Database</th><td>MySQL</td></tr>
        <tr><th>Server Time</th><td><?php echo date('Y-m-d H:i:s'); ?></td></tr>
        <tr><th>Operating System</th><td><?php echo PHP_OS; ?></td></tr>
    </table>
</div>
<?php
gp_page_footer();
