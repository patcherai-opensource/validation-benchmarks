<?php
/**
 * Dolibarr ERP & CRM - Administration home
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

llxHeader('System information', $user);
?>
<div class="side-container">
<?php printUserAdminSidebar(); ?>
<div class="main-content">
    <div class="breadcrumb"><a href="/admin/index.php">Home</a> &gt; System information</div>

    <?php dol_htmloutput_events(); ?>

    <h2 class="titre">System information</h2>

    <div class="fiche">
        <table class="border">
            <tr>
                <td class="titlefield">Application</td>
                <td>Dolibarr ERP/CRM</td>
            </tr>
            <tr>
                <td class="titlefield">Version</td>
                <td>19.0.1</td>
            </tr>
            <tr>
                <td class="titlefield">PHP Version</td>
                <td><?php echo dol_escape_htmltag(phpversion()); ?></td>
            </tr>
            <tr>
                <td class="titlefield">Web server</td>
                <td><?php echo dol_escape_htmltag($_SERVER['SERVER_SOFTWARE'] ?? 'Apache'); ?></td>
            </tr>
            <tr>
                <td class="titlefield">Database</td>
                <td>MySQL</td>
            </tr>
            <tr>
                <td class="titlefield">Operating System</td>
                <td><?php echo dol_escape_htmltag(php_uname('s').' '.php_uname('r')); ?></td>
            </tr>
        </table>
    </div>

    <h2 class="titre">Quick links</h2>
    <div class="fiche">
        <ul style="list-style: none; padding: 0;">
            <li style="padding: 5px 0;"><a href="/user/index.php">&#x1F464; Users list</a></li>
            <li style="padding: 5px 0;"><a href="/user/admin/user_extrafields.php">&#x2699; User extra fields setup</a></li>
            <li style="padding: 5px 0;"><a href="/admin/modules.php">&#x1F4E6; Modules</a></li>
        </ul>
    </div>
</div>
</div>
<?php
llxFooter();
