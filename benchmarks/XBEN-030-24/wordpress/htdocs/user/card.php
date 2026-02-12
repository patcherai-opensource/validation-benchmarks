<?php
/**
 * Dolibarr ERP & CRM - User card
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

$id = GETPOSTINT('id');
if (empty($id)) {
    header('Location: /user/index.php');
    exit;
}

// Load extra fields definitions
$extrafields->fetch_name_optionals_label('user');

// Load the user
$edituser = new User($db);
$result = $edituser->fetch($id);
if ($result <= 0) {
    header('Location: /user/index.php');
    exit;
}

llxHeader('User - '.$edituser->getFullName(), $user);
?>
<div class="side-container">
<?php printUserAdminSidebar(); ?>
<div class="main-content">
    <div class="breadcrumb"><a href="/admin/index.php">Home</a> &gt; <a href="/user/index.php">Users list</a> &gt; <?php echo dol_escape_htmltag($edituser->getFullName()); ?></div>

    <?php dol_htmloutput_events(); ?>

    <div class="tabs">
        <a href="/user/card.php?id=<?php echo $id; ?>" class="active">User card</a>
    </div>

    <div class="fiche">
        <table class="border">
            <tr>
                <td class="titlefield">Ref</td>
                <td><?php echo (int)$edituser->id; ?></td>
            </tr>
            <tr>
                <td class="titlefield">Login</td>
                <td><?php echo dol_escape_htmltag($edituser->login); ?></td>
            </tr>
            <tr>
                <td class="titlefield">Last Name</td>
                <td><?php echo dol_escape_htmltag($edituser->lastname); ?></td>
            </tr>
            <tr>
                <td class="titlefield">First Name</td>
                <td><?php echo dol_escape_htmltag($edituser->firstname); ?></td>
            </tr>
            <tr>
                <td class="titlefield">Email</td>
                <td><?php echo dol_escape_htmltag($edituser->email); ?></td>
            </tr>
            <tr>
                <td class="titlefield">Job / Position</td>
                <td><?php echo dol_escape_htmltag($edituser->job); ?></td>
            </tr>
            <tr>
                <td class="titlefield">Phone</td>
                <td><?php echo dol_escape_htmltag($edituser->office_phone); ?></td>
            </tr>
            <tr>
                <td class="titlefield">Mobile</td>
                <td><?php echo dol_escape_htmltag($edituser->user_mobile); ?></td>
            </tr>
            <tr>
                <td class="titlefield">Address</td>
                <td><?php echo dol_escape_htmltag($edituser->address); ?></td>
            </tr>
            <tr>
                <td class="titlefield">Zip / Town</td>
                <td><?php echo dol_escape_htmltag($edituser->zip); ?> <?php echo dol_escape_htmltag($edituser->town); ?></td>
            </tr>
            <tr>
                <td class="titlefield">Admin</td>
                <td><?php echo $edituser->admin ? '<span class="badge badge-status5">Yes</span>' : 'No'; ?></td>
            </tr>
            <tr>
                <td class="titlefield">Status</td>
                <td><?php echo $edituser->statut ? '<span class="badge badge-status1">Active</span>' : '<span class="badge badge-status0">Disabled</span>'; ?></td>
            </tr>
            <tr>
                <td class="titlefield">Created</td>
                <td><?php echo dol_escape_htmltag(dol_print_date(strtotime($edituser->datec))); ?></td>
            </tr>
            <?php
            // Display extra fields
            echo $edituser->showOptionals($extrafields, 'view');
            ?>
        </table>
    </div>

    <div style="margin-top: 15px;">
        <a class="butAction" href="/user/index.php">Back to list</a>
    </div>
</div>
</div>
<?php
llxFooter();
