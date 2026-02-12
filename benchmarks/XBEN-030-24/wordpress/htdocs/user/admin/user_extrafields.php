<?php
/**
 * Dolibarr ERP & CRM - User extra fields setup
 *
 * Page to configure extra attributes for User module.
 * Accessible only to administrators.
 *
 * @package  Dolibarr\User\Admin
 */

require_once __DIR__.'/../../master.inc.php';
require_once __DIR__.'/../../core/lib/admin.lib.php';
require_once __DIR__.'/../../core/class/extrafields.class.php';

// Access control - only admins
if (empty($user) || empty($user->id) || empty($user->admin)) {
    header('Location: /index.php?error=access_denied');
    exit;
}

$elementtype = 'user';
$action = GETPOST('action');
$token = GETPOST('token');

// Verify token for write actions
$tokenok = (!empty($token) && $token == $_SESSION['newtoken']);

// Handle actions
if ($action == 'add' && $tokenok) {
    $attrname = GETPOST('attrname');
    $label    = GETPOST('label');
    $type     = GETPOST('type');
    $size     = GETPOST('size');
    $computed = GETPOST('computed');
    $pos      = GETPOSTINT('pos', 100);
    $required = GETPOSTINT('required');
    $enabled  = GETPOSTINT('enabled', 1);
    $list     = GETPOSTINT('list', 1);
    $help     = GETPOST('help');
    $default  = GETPOST('default_value');

    $result = $extrafields->addExtraField($attrname, $label, $type, $pos, $size, $elementtype, $required, $default, $computed, $enabled, $list, $help);

    if ($result > 0) {
        setEventMessages('Extra field added successfully', null, 'mesgs');
        header('Location: /user/admin/user_extrafields.php');
        exit;
    } else {
        setEventMessages($extrafields->error, null, 'errors');
    }
}

if ($action == 'update' && $tokenok) {
    $attrname = GETPOST('attrname');
    $label    = GETPOST('label');
    $type     = GETPOST('type');
    $size     = GETPOST('size');
    $computed = GETPOST('computed');
    $pos      = GETPOSTINT('pos', 100);
    $required = GETPOSTINT('required');
    $enabled  = GETPOSTINT('enabled', 1);
    $list     = GETPOSTINT('list', 1);
    $help     = GETPOST('help');
    $default  = GETPOST('default_value');

    $result = $extrafields->updateExtraField($attrname, $label, $type, $pos, $size, $elementtype, $required, $default, $computed, $enabled, $list, $help);

    if ($result > 0) {
        setEventMessages('Extra field updated successfully', null, 'mesgs');
        header('Location: /user/admin/user_extrafields.php');
        exit;
    } else {
        setEventMessages($extrafields->error, null, 'errors');
    }
}

if ($action == 'delete' && $tokenok) {
    $attrname = GETPOST('attrname');
    $result = $extrafields->deleteExtraField($attrname, $elementtype);
    if ($result > 0) {
        setEventMessages('Extra field deleted', null, 'mesgs');
    } else {
        setEventMessages($extrafields->error, null, 'errors');
    }
    header('Location: /user/admin/user_extrafields.php');
    exit;
}

// Load current extra fields
$extrafields->fetch_name_optionals_label($elementtype, true);

// Generate token
$token = newToken();

llxHeader('Users - Supplementary attributes', $user);
?>
<div class="side-container">
<?php printUserAdminSidebar(); ?>
<div class="main-content">
    <div class="breadcrumb"><a href="/admin/index.php">Home</a> &gt; <a href="/user/index.php">Users</a> &gt; Extra fields setup</div>

    <?php dol_htmloutput_events(); ?>

    <div class="tabs">
        <a href="/user/index.php">Users list</a>
        <a href="/user/admin/user_extrafields.php" class="active">Supplementary attributes</a>
    </div>

    <h2 class="titre">Supplementary attributes for Users</h2>

    <!-- List existing extra fields -->
    <div class="fiche">
        <table class="liste">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Label</th>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Computed value</th>
                    <th>Position</th>
                    <th>Enabled</th>
                    <th>Required</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php
                if (!empty($extrafields->attributes[$elementtype]['label'])) {
                    foreach ($extrafields->attributes[$elementtype]['label'] as $key => $label) {
                        $type     = $extrafields->attributes[$elementtype]['type'][$key];
                        $size     = $extrafields->attributes[$elementtype]['size'][$key];
                        $computed = $extrafields->attributes[$elementtype]['computed'][$key];
                        $pos      = $extrafields->attributes[$elementtype]['pos'][$key];
                        $enabled  = $extrafields->attributes[$elementtype]['enabled'][$key];
                        $required = $extrafields->attributes[$elementtype]['required'][$key];
                        ?>
                        <tr>
                            <td><strong><?php echo dol_escape_htmltag($key); ?></strong></td>
                            <td><?php echo dol_escape_htmltag($label); ?></td>
                            <td><?php echo dol_escape_htmltag($type); ?></td>
                            <td><?php echo dol_escape_htmltag($size); ?></td>
                            <td><code style="font-size:11px;color:#666;"><?php echo dol_escape_htmltag($computed ?: '-'); ?></code></td>
                            <td><?php echo (int) $pos; ?></td>
                            <td><?php echo $enabled ? 'Yes' : 'No'; ?></td>
                            <td><?php echo $required ? 'Yes' : 'No'; ?></td>
                            <td>
                                <a href="#editform" onclick="document.getElementById('edit_attrname').value='<?php echo dol_escape_htmltag($key, 2); ?>';document.getElementById('edit_label').value='<?php echo dol_escape_htmltag($label, 2); ?>';document.getElementById('edit_type').value='<?php echo dol_escape_htmltag($type, 2); ?>';document.getElementById('edit_size').value='<?php echo dol_escape_htmltag($size, 2); ?>';document.getElementById('edit_computed').value='<?php echo dol_escape_htmltag($computed, 2); ?>';document.getElementById('edit_pos').value='<?php echo (int)$pos; ?>';document.getElementById('edit_enabled').value='<?php echo (int)$enabled; ?>';document.getElementById('edit_required').value='<?php echo (int)$required; ?>';document.getElementById('editform').style.display='block';return false;">Edit</a>
                                &nbsp;
                                <a href="/user/admin/user_extrafields.php?action=delete&attrname=<?php echo urlencode($key); ?>&token=<?php echo urlencode($token); ?>" onclick="return confirm('Are you sure you want to delete this extra field?');" style="color:#bc3434;">Delete</a>
                            </td>
                        </tr>
                        <?php
                    }
                } else {
                    echo '<tr><td colspan="9" style="text-align: center; color: #999; padding: 20px;">No supplementary attributes defined</td></tr>';
                }
                ?>
            </tbody>
        </table>
    </div>

    <!-- Edit form (hidden by default) -->
    <div id="editform" style="display:none;">
        <h2 class="titre">Modify an attribute</h2>
        <div class="fiche">
            <form method="post" action="/user/admin/user_extrafields.php">
                <input type="hidden" name="action" value="update">
                <input type="hidden" name="token" value="<?php echo dol_escape_htmltag($token); ?>">
                <table class="border">
                    <tr>
                        <td class="titlefield">Attribute code</td>
                        <td><input type="text" name="attrname" id="edit_attrname" class="flat" readonly style="background:#eee;"></td>
                    </tr>
                    <tr>
                        <td class="titlefield">Label</td>
                        <td><input type="text" name="label" id="edit_label" class="flat"></td>
                    </tr>
                    <tr>
                        <td class="titlefield">Type</td>
                        <td>
                            <select name="type" id="edit_type" class="flat">
                                <option value="varchar">String (varchar)</option>
                                <option value="int">Integer</option>
                                <option value="double">Float</option>
                                <option value="text">Text</option>
                                <option value="date">Date</option>
                                <option value="boolean">Boolean</option>
                                <option value="computed">Computed</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <td class="titlefield">Size</td>
                        <td><input type="text" name="size" id="edit_size" class="flat" style="width:80px;"></td>
                    </tr>
                    <tr>
                        <td class="titlefield">Computed value<br><span style="font-size:11px;color:#888;">PHP expression for computed fields. Example: <code>$object->id * 2</code></span></td>
                        <td><textarea name="computed" id="edit_computed" class="flat" rows="3"></textarea></td>
                    </tr>
                    <tr>
                        <td class="titlefield">Position</td>
                        <td><input type="text" name="pos" id="edit_pos" class="flat" style="width:60px;"></td>
                    </tr>
                    <tr>
                        <td class="titlefield">Enabled</td>
                        <td>
                            <select name="enabled" id="edit_enabled" class="flat">
                                <option value="1">Yes</option>
                                <option value="0">No</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <td class="titlefield">Required</td>
                        <td>
                            <select name="required" id="edit_required" class="flat">
                                <option value="0">No</option>
                                <option value="1">Yes</option>
                            </select>
                        </td>
                    </tr>
                </table>
                <div style="margin-top: 10px;">
                    <button type="submit" class="button">Save changes</button>
                    <a href="#" onclick="document.getElementById('editform').style.display='none';return false;" style="margin-left:10px;">Cancel</a>
                </div>
            </form>
        </div>
    </div>

    <!-- Add new extra field form -->
    <h2 class="titre">Add a new attribute</h2>
    <div class="fiche">
        <form method="post" action="/user/admin/user_extrafields.php">
            <input type="hidden" name="action" value="add">
            <input type="hidden" name="token" value="<?php echo dol_escape_htmltag($token); ?>">
            <table class="border">
                <tr>
                    <td class="titlefield">Attribute code <span style="color:red;">*</span></td>
                    <td><input type="text" name="attrname" class="flat" placeholder="e.g. department" required pattern="[a-zA-Z][a-zA-Z0-9_]*"></td>
                </tr>
                <tr>
                    <td class="titlefield">Label <span style="color:red;">*</span></td>
                    <td><input type="text" name="label" class="flat" placeholder="e.g. Department" required></td>
                </tr>
                <tr>
                    <td class="titlefield">Type <span style="color:red;">*</span></td>
                    <td>
                        <select name="type" class="flat" id="add_type" onchange="document.getElementById('add_computed_row').style.display=(this.value=='computed'?'':'none');">
                            <option value="varchar">String (varchar)</option>
                            <option value="int">Integer</option>
                            <option value="double">Float</option>
                            <option value="text">Text</option>
                            <option value="date">Date</option>
                            <option value="boolean">Boolean</option>
                            <option value="computed">Computed</option>
                        </select>
                    </td>
                </tr>
                <tr>
                    <td class="titlefield">Size</td>
                    <td><input type="text" name="size" class="flat" style="width:80px;" value="255"></td>
                </tr>
                <tr id="add_computed_row" style="display:none;">
                    <td class="titlefield">Computed value<br><span style="font-size:11px;color:#888;">PHP expression for value computation.<br>Use <code>$object</code> to access current record.<br>Example: <code>$object->id * 2</code></span></td>
                    <td><textarea name="computed" class="flat" rows="3" placeholder="PHP expression..."></textarea></td>
                </tr>
                <tr>
                    <td class="titlefield">Default value</td>
                    <td><input type="text" name="default_value" class="flat"></td>
                </tr>
                <tr>
                    <td class="titlefield">Position</td>
                    <td><input type="text" name="pos" class="flat" style="width:60px;" value="100"></td>
                </tr>
                <tr>
                    <td class="titlefield">Enabled</td>
                    <td>
                        <select name="enabled" class="flat">
                            <option value="1" selected>Yes</option>
                            <option value="0">No</option>
                        </select>
                    </td>
                </tr>
                <tr>
                    <td class="titlefield">Required</td>
                    <td>
                        <select name="required" class="flat">
                            <option value="0" selected>No</option>
                            <option value="1">Yes</option>
                        </select>
                    </td>
                </tr>
                <tr>
                    <td class="titlefield">Help text</td>
                    <td><input type="text" name="help" class="flat" style="width: 400px;"></td>
                </tr>
            </table>
            <div style="margin-top: 10px;">
                <button type="submit" class="button">Add attribute</button>
            </div>
        </form>
    </div>

</div>
</div>
<?php
llxFooter();
