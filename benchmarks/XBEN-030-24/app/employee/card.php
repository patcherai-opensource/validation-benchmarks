<?php
/**
 * Employee detail card - shows employee info including computed custom fields
 */

$id = intval(gp_get_post('id', 0));
if ($id <= 0) {
    gp_redirect('/index.php?module=employee&action=list');
}

$db = get_db();
$emp = new Employee($db);
if ($emp->load($id) < 0) {
    gp_page_header('Employee Not Found');
    gp_show_message('Employee not found.', 'error');
    gp_page_footer();
    exit;
}

$customfields = new CustomFields($db);
$customfields->loadDefs('employee');
$emp->loadCustomData($customfields);

gp_page_header('Employee - ' . $emp->firstname . ' ' . $emp->lastname);
?>
<div class="gp-content">
    <?php gp_page_title($emp->firstname . ' ' . $emp->lastname, '/index.php?module=employee&action=list'); ?>

    <div class="gp-detail-card">
        <table class="gp-table gp-detail-table">
            <tr><th>Employee ID</th><td><?php echo intval($emp->id); ?></td></tr>
            <tr><th>First Name</th><td><?php echo gp_escape_html($emp->firstname); ?></td></tr>
            <tr><th>Last Name</th><td><?php echo gp_escape_html($emp->lastname); ?></td></tr>
            <tr><th>Email</th><td><?php echo gp_escape_html($emp->email); ?></td></tr>
            <tr><th>Job Title</th><td><?php echo gp_escape_html($emp->job_title); ?></td></tr>
            <tr><th>Department</th><td><?php echo gp_escape_html($emp->department); ?></td></tr>
            <tr><th>Hire Date</th><td><?php echo gp_escape_html($emp->hire_date); ?></td></tr>
            <tr><th>Salary</th><td><?php echo number_format((float)$emp->salary, 2); ?></td></tr>
            <tr><th>Status</th><td><?php echo $emp->status ? 'Active' : 'Inactive'; ?></td></tr>
        </table>

        <?php if (!empty($customfields->attributes['employee']['label'])): ?>
        <h3>Custom Fields</h3>
        <table class="gp-table gp-detail-table">
            <?php foreach ($customfields->attributes['employee']['label'] as $key => $label): ?>
            <tr>
                <th><?php echo gp_escape_html($label); ?></th>
                <td><?php echo gp_escape_html($emp->custom_values[$key] ?? ''); ?></td>
            </tr>
            <?php endforeach; ?>
        </table>
        <?php endif; ?>
    </div>
</div>
<?php
gp_page_footer();
