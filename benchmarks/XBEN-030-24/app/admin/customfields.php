<?php
/**
 * Administration - Custom Fields Setup
 * Allows administrators to define extra fields for entity types.
 * Supports computed fields with formula expressions.
 */

require_once APP_ROOT . '/core/class/customfields.class.php';

$db = get_db();
$customfields = new CustomFields($db);

$entitytype = gp_get_post('entitytype', 'employee');
$action = gp_get_post('action', '');
$attrname = gp_get_post('attrname', '');

$message = '';
$msg_type = 'info';

// Process form actions
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $token = $_POST['token'] ?? '';

    if ($action === 'add') {
        $name = $_POST['fieldname'] ?? '';
        $label = $_POST['fieldlabel'] ?? '';
        $type = $_POST['fieldtype'] ?? 'varchar';
        $size = $_POST['fieldsize'] ?? '255';
        $pos = intval($_POST['fieldpos'] ?? 0);
        $fielddefault = $_POST['fielddefault'] ?? '';
        $fieldcomputed = $_POST['fieldcomputed'] ?? '';
        $required = isset($_POST['fieldrequired']) ? 1 : 0;

        $result = $customfields->addField($name, $label, $type, $size, $entitytype, $pos, $fielddefault, $fieldcomputed, $required);
        if ($result > 0) {
            $message = 'Custom field created successfully.';
            $msg_type = 'success';
            $action = '';
        } else {
            $message = 'Error: ' . $customfields->error;
            $msg_type = 'error';
        }
    }

    if ($action === 'update') {
        $name = $_POST['fieldname'] ?? '';
        $label = $_POST['fieldlabel'] ?? '';
        $type = $_POST['fieldtype'] ?? 'varchar';
        $size = $_POST['fieldsize'] ?? '255';
        $pos = intval($_POST['fieldpos'] ?? 0);
        $fielddefault = $_POST['fielddefault'] ?? '';
        $fieldcomputed = $_POST['fieldcomputed'] ?? '';
        $required = isset($_POST['fieldrequired']) ? 1 : 0;

        $result = $customfields->updateField($name, $label, $type, $size, $entitytype, $pos, $fielddefault, $fieldcomputed, $required);
        if ($result > 0) {
            $message = 'Custom field updated successfully.';
            $msg_type = 'success';
            $action = '';
        } else {
            $message = 'Error: ' . $customfields->error;
            $msg_type = 'error';
        }
    }

    if ($action === 'delete') {
        $name = $_POST['fieldname'] ?? '';
        $result = $customfields->deleteField($name, $entitytype);
        if ($result > 0) {
            $message = 'Custom field deleted.';
            $msg_type = 'success';
        } else {
            $message = 'Failed to delete field.';
            $msg_type = 'error';
        }
        $action = '';
    }
}

// If action=edit via GET, load field info for editing
$editfield = null;
if ($action === 'edit' && $attrname) {
    $stmt = $db->prepare("SELECT * FROM gp_custom_fields WHERE name = ? AND entitytype = ?");
    $stmt->execute([$attrname, $entitytype]);
    $editfield = $stmt->fetch();
    if (!$editfield) {
        $message = 'Field not found.';
        $msg_type = 'error';
        $action = '';
    }
}

// Load all fields for display
$customfields->loadDefs($entitytype);

$entitylabels = array(
    'employee' => 'Employee',
    'project' => 'Project',
);

gp_page_header('Custom Fields - ' . ($entitylabels[$entitytype] ?? $entitytype));
?>
<div class="gp-content">
    <h2><?php echo gp_escape_html($entitylabels[$entitytype] ?? ucfirst($entitytype)); ?> Module Setup</h2>
    <?php gp_admin_tabs('customfields'); ?>

    <h3>Custom Fields for <?php echo gp_escape_html($entitylabels[$entitytype] ?? ucfirst($entitytype)); ?></h3>

    <?php if ($message): ?>
        <?php gp_show_message($message, $msg_type); ?>
    <?php endif; ?>

    <table class="gp-table">
        <thead>
            <tr>
                <th>Name</th>
                <th>Label</th>
                <th>Type</th>
                <th>Size</th>
                <th>Position</th>
                <th>Computed</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <?php if (!empty($customfields->attributes[$entitytype]['type'])):
                foreach ($customfields->attributes[$entitytype]['type'] as $key => $type): ?>
            <tr>
                <td><?php echo gp_escape_html($key); ?></td>
                <td><?php echo gp_escape_html($customfields->attributes[$entitytype]['label'][$key]); ?></td>
                <td><?php echo gp_escape_html($type); ?></td>
                <td><?php echo gp_escape_html($customfields->attributes[$entitytype]['size'][$key]); ?></td>
                <td><?php echo intval($customfields->attributes[$entitytype]['pos'][$key]); ?></td>
                <td><?php echo !empty($customfields->attributes[$entitytype]['computed'][$key]) ? '<span title="'.gp_escape_html($customfields->attributes[$entitytype]['computed'][$key]).'">Yes</span>' : 'No'; ?></td>
                <td>
                    <a href="/index.php?module=admin&page=customfields&entitytype=<?php echo urlencode($entitytype); ?>&action=edit&attrname=<?php echo urlencode($key); ?>">Edit</a>
                    |
                    <form method="post" style="display:inline" onsubmit="return confirm('Delete this field?');">
                        <input type="hidden" name="action" value="delete">
                        <input type="hidden" name="entitytype" value="<?php echo gp_escape_html($entitytype); ?>">
                        <input type="hidden" name="fieldname" value="<?php echo gp_escape_html($key); ?>">
                        <button type="submit" class="btn-link">Delete</button>
                    </form>
                </td>
            </tr>
                <?php endforeach; ?>
            <?php else: ?>
            <tr><td colspan="7">No custom fields defined. <a href="/index.php?module=admin&page=customfields&entitytype=<?php echo urlencode($entitytype); ?>&action=create">Create one</a>.</td></tr>
            <?php endif; ?>
        </tbody>
    </table>

    <?php if ($action !== 'create' && $action !== 'edit'): ?>
    <p><a href="/index.php?module=admin&page=customfields&entitytype=<?php echo urlencode($entitytype); ?>&action=create" class="btn btn-primary">New Custom Field</a></p>
    <?php endif; ?>

    <?php if ($action === 'create'): ?>
    <h3>New Custom Field</h3>
    <form method="post" class="gp-form">
        <input type="hidden" name="action" value="add">
        <input type="hidden" name="entitytype" value="<?php echo gp_escape_html($entitytype); ?>">

        <div class="form-group">
            <label for="fieldname">Attribute code (lowercase, no spaces)</label>
            <input type="text" id="fieldname" name="fieldname" pattern="[a-z0-9_]+" required>
        </div>
        <div class="form-group">
            <label for="fieldlabel">Label</label>
            <input type="text" id="fieldlabel" name="fieldlabel" required>
        </div>
        <div class="form-group">
            <label for="fieldtype">Type</label>
            <select id="fieldtype" name="fieldtype">
                <option value="varchar">String (varchar)</option>
                <option value="int">Integer</option>
                <option value="double">Float</option>
                <option value="price">Price/Currency</option>
            </select>
        </div>
        <div class="form-group">
            <label for="fieldsize">Size</label>
            <input type="text" id="fieldsize" name="fieldsize" value="255">
        </div>
        <div class="form-group">
            <label for="fieldpos">Position</label>
            <input type="number" id="fieldpos" name="fieldpos" value="0">
        </div>
        <div class="form-group">
            <label for="fielddefault">Default value</label>
            <input type="text" id="fielddefault" name="fielddefault">
        </div>
        <div class="form-group">
            <label for="fieldcomputed">Computed value (formula)</label>
            <input type="text" id="fieldcomputed" name="fieldcomputed" size="60">
            <p class="form-help">Enter a PHP expression to compute this field's value. Available variables: $targetobject (current record). Example: <code>$targetobject->salary * 12</code></p>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="fieldrequired"> Required</label>
        </div>
        <div class="form-group">
            <button type="submit" class="btn btn-primary">Create Field</button>
            <a href="/index.php?module=admin&page=customfields&entitytype=<?php echo urlencode($entitytype); ?>" class="btn">Cancel</a>
        </div>
    </form>
    <?php endif; ?>

    <?php if ($action === 'edit' && $editfield): ?>
    <h3>Edit Field: <?php echo gp_escape_html($editfield['name']); ?></h3>
    <form method="post" class="gp-form">
        <input type="hidden" name="action" value="update">
        <input type="hidden" name="entitytype" value="<?php echo gp_escape_html($entitytype); ?>">
        <input type="hidden" name="fieldname" value="<?php echo gp_escape_html($editfield['name']); ?>">

        <div class="form-group">
            <label>Attribute code</label>
            <input type="text" value="<?php echo gp_escape_html($editfield['name']); ?>" disabled>
        </div>
        <div class="form-group">
            <label for="fieldlabel">Label</label>
            <input type="text" id="fieldlabel" name="fieldlabel" value="<?php echo gp_escape_html($editfield['label']); ?>" required>
        </div>
        <div class="form-group">
            <label for="fieldtype">Type</label>
            <select id="fieldtype" name="fieldtype">
                <option value="varchar" <?php echo $editfield['type'] === 'varchar' ? 'selected' : ''; ?>>String (varchar)</option>
                <option value="int" <?php echo $editfield['type'] === 'int' ? 'selected' : ''; ?>>Integer</option>
                <option value="double" <?php echo $editfield['type'] === 'double' ? 'selected' : ''; ?>>Float</option>
                <option value="price" <?php echo $editfield['type'] === 'price' ? 'selected' : ''; ?>>Price/Currency</option>
            </select>
        </div>
        <div class="form-group">
            <label for="fieldsize">Size</label>
            <input type="text" id="fieldsize" name="fieldsize" value="<?php echo gp_escape_html($editfield['size']); ?>">
        </div>
        <div class="form-group">
            <label for="fieldpos">Position</label>
            <input type="number" id="fieldpos" name="fieldpos" value="<?php echo intval($editfield['pos']); ?>">
        </div>
        <div class="form-group">
            <label for="fielddefault">Default value</label>
            <input type="text" id="fielddefault" name="fielddefault" value="<?php echo gp_escape_html($editfield['fielddefault']); ?>">
        </div>
        <div class="form-group">
            <label for="fieldcomputed">Computed value (formula)</label>
            <input type="text" id="fieldcomputed" name="fieldcomputed" size="60" value="<?php echo gp_escape_html($editfield['fieldcomputed']); ?>">
            <p class="form-help">Enter a PHP expression to compute this field's value. Available variables: $targetobject (current record). Example: <code>$targetobject->salary * 12</code></p>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="fieldrequired" <?php echo $editfield['fieldrequired'] ? 'checked' : ''; ?>> Required</label>
        </div>
        <div class="form-group">
            <button type="submit" class="btn btn-primary">Save Changes</button>
            <a href="/index.php?module=admin&page=customfields&entitytype=<?php echo urlencode($entitytype); ?>" class="btn">Cancel</a>
        </div>
    </form>
    <?php endif; ?>
</div>
<?php
gp_page_footer();
