<?php
/**
 * Dolibarr ERP & CRM - Users list
 *
 * @package  Dolibarr\User
 */

require_once __DIR__.'/../master.inc.php';
require_once __DIR__.'/../core/lib/admin.lib.php';
require_once __DIR__.'/class/user.class.php';

// Access control
if (empty($user) || empty($user->id)) {
    header('Location: /index.php?error=access_denied');
    exit;
}

// Load extra fields definitions
$extrafields->fetch_name_optionals_label('user');

// Get users list
$sql = "SELECT u.rowid, u.login, u.lastname, u.firstname, u.email, u.admin, u.statut, u.datec";
$sql .= " FROM ".$db->prefix."user as u";
$sql .= " WHERE u.entity IN (0, 1)";
$sql .= " ORDER BY u.lastname ASC, u.firstname ASC";

$result = $db->query($sql);
$users = array();
if ($result) {
    while ($obj = $db->fetch_object($result)) {
        // Also fetch extra fields for each user
        $tmpuser = new User($db);
        $tmpuser->id = $obj->rowid;
        $tmpuser->login = $obj->login;
        $tmpuser->lastname = $obj->lastname;
        $tmpuser->firstname = $obj->firstname;
        $tmpuser->email = $obj->email;
        $tmpuser->admin = $obj->admin;
        $tmpuser->statut = $obj->statut;
        $tmpuser->datec = $obj->datec;
        $tmpuser->fetch_optionals($obj->rowid);
        $users[] = $tmpuser;
    }
    $db->free($result);
}

llxHeader('Users', $user);
?>
<div class="side-container">
<?php printUserAdminSidebar(); ?>
<div class="main-content">
    <div class="breadcrumb"><a href="/admin/index.php">Home</a> &gt; Users &amp; Groups &gt; Users list</div>

    <?php dol_htmloutput_events(); ?>

    <h2 class="titre">Users list</h2>

    <div class="fiche">
        <table class="liste">
            <thead>
                <tr>
                    <th>Login</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Admin</th>
                    <th>Status</th>
                    <th>Created</th>
                    <?php
                    // Display extra field columns
                    if (!empty($extrafields->attributes['user']['label'])) {
                        foreach ($extrafields->attributes['user']['label'] as $key => $label) {
                            echo '<th>'.dol_escape_htmltag($label).'</th>';
                        }
                    }
                    ?>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($users as $u) { ?>
                <tr>
                    <td><a href="/user/card.php?id=<?php echo (int)$u->id; ?>"><?php echo dol_escape_htmltag($u->login); ?></a></td>
                    <td><?php echo dol_escape_htmltag($u->getFullName()); ?></td>
                    <td><?php echo dol_escape_htmltag($u->email); ?></td>
                    <td><?php echo $u->admin ? '<span class="badge badge-status5">Yes</span>' : 'No'; ?></td>
                    <td><?php echo $u->statut ? '<span class="badge badge-status1">Active</span>' : '<span class="badge badge-status0">Disabled</span>'; ?></td>
                    <td><?php echo dol_escape_htmltag(dol_print_date(strtotime($u->datec), 'Y-m-d')); ?></td>
                    <?php
                    // Display extra field values
                    if (!empty($extrafields->attributes['user']['label'])) {
                        foreach ($extrafields->attributes['user']['label'] as $key => $label) {
                            $val = isset($u->array_options['options_'.$key]) ? $u->array_options['options_'.$key] : '';
                            echo '<td>'.dol_escape_htmltag($val).'</td>';
                        }
                    }
                    ?>
                </tr>
                <?php } ?>
                <?php if (empty($users)) { ?>
                <tr><td colspan="6" style="text-align: center; color: #999; padding: 20px;">No users found</td></tr>
                <?php } ?>
            </tbody>
        </table>
    </div>
</div>
</div>
<?php
llxFooter();
