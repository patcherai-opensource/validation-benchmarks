<?php
/**
 * Administration - Module Management
 */

gp_page_header('Administration - Modules');
?>
<div class="gp-content">
    <h2>Administration</h2>
    <?php gp_admin_tabs('modules'); ?>

    <h3>Module Configuration</h3>
    <table class="gp-table">
        <thead>
            <tr>
                <th>Module</th>
                <th>Description</th>
                <th>Status</th>
                <th>Setup</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Employees (HR)</td>
                <td>Employee management, directory, and HR functions</td>
                <td><span class="status-active">Enabled</span></td>
                <td><a href="/index.php?module=admin&page=customfields&entitytype=employee">Custom Fields</a></td>
            </tr>
            <tr>
                <td>Projects</td>
                <td>Project tracking and management</td>
                <td><span class="status-active">Enabled</span></td>
                <td><a href="/index.php?module=admin&page=customfields&entitytype=project">Custom Fields</a></td>
            </tr>
            <tr>
                <td>Invoicing</td>
                <td>Invoice generation and billing management</td>
                <td><span class="status-inactive">Disabled</span></td>
                <td>-</td>
            </tr>
            <tr>
                <td>Inventory</td>
                <td>Stock and warehouse management</td>
                <td><span class="status-inactive">Disabled</span></td>
                <td>-</td>
            </tr>
        </tbody>
    </table>
</div>
<?php
gp_page_footer();
