<?php
/**
 * Dolibarr ERP & CRM - Modules setup
 *
 * @package  Dolibarr\Admin
 */

require_once __DIR__.'/../master.inc.php';
require_once __DIR__.'/../core/lib/admin.lib.php';

// Access control
if (empty($user) || empty($user->id)) {
    header('Location: /index.php?error=access_denied');
    exit;
}

llxHeader('Modules setup', $user);
?>
<div class="side-container">
<?php printUserAdminSidebar(); ?>
<div class="main-content">
    <div class="breadcrumb"><a href="/admin/index.php">Home</a> &gt; Modules</div>

    <h2 class="titre">Modules / Applications setup</h2>

    <div class="fiche">
        <table class="liste">
            <thead>
                <tr>
                    <th>Module</th>
                    <th>Description</th>
                    <th>Version</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Users & Groups</strong></td>
                    <td>User, group, and permission management</td>
                    <td>19.0.1</td>
                    <td><span class="badge badge-status1">Enabled</span></td>
                </tr>
                <tr>
                    <td><strong>Third Parties</strong></td>
                    <td>Customers, prospects, and suppliers management</td>
                    <td>19.0.1</td>
                    <td><span class="badge badge-status1">Enabled</span></td>
                </tr>
                <tr>
                    <td><strong>Invoices</strong></td>
                    <td>Customer and supplier invoices management</td>
                    <td>19.0.1</td>
                    <td><span class="badge badge-status1">Enabled</span></td>
                </tr>
                <tr>
                    <td><strong>Products / Services</strong></td>
                    <td>Products and services catalog</td>
                    <td>19.0.1</td>
                    <td><span class="badge badge-status1">Enabled</span></td>
                </tr>
                <tr>
                    <td><strong>HRM</strong></td>
                    <td>Human resources management</td>
                    <td>19.0.1</td>
                    <td><span class="badge badge-status1">Enabled</span></td>
                </tr>
                <tr>
                    <td><strong>Projects</strong></td>
                    <td>Project and task management</td>
                    <td>19.0.1</td>
                    <td><span class="badge badge-status0">Disabled</span></td>
                </tr>
                <tr>
                    <td><strong>Stock / Warehouse</strong></td>
                    <td>Warehouse and stock management</td>
                    <td>19.0.1</td>
                    <td><span class="badge badge-status0">Disabled</span></td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
</div>
<?php
llxFooter();
