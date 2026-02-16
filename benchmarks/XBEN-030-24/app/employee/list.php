<?php
/**
 * Employee list page - displays all employees with their custom fields
 * Computed custom fields are evaluated here during rendering
 */

$db = get_db();
$employees = Employee::listAll($db);

$customfields = new CustomFields($db);
$customfields->loadDefs('employee');

gp_page_header('Employee List');
?>
<div class="gp-content">
    <h2>Employee Directory</h2>
    <table class="gp-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Last Name</th>
                <th>First Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Job Title</th>
                <th>Status</th>
                <?php
                if (!empty($customfields->attributes['employee']['label'])) {
                    foreach ($customfields->attributes['employee']['label'] as $key => $label) {
                        echo '<th>' . gp_escape_html($label) . '</th>';
                    }
                }
                ?>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($employees as $row):
                $emp = new Employee($db);
                $emp->load($row['rowid']);
                $emp->loadCustomData($customfields);
            ?>
            <tr>
                <td><a href="/index.php?module=employee&action=view&id=<?php echo intval($emp->id); ?>"><?php echo intval($emp->id); ?></a></td>
                <td><?php echo gp_escape_html($emp->lastname); ?></td>
                <td><?php echo gp_escape_html($emp->firstname); ?></td>
                <td><?php echo gp_escape_html($emp->email); ?></td>
                <td><?php echo gp_escape_html($emp->department); ?></td>
                <td><?php echo gp_escape_html($emp->job_title); ?></td>
                <td><?php echo $emp->status ? '<span class="status-active">Active</span>' : '<span class="status-inactive">Inactive</span>'; ?></td>
                <?php
                if (!empty($customfields->attributes['employee']['label'])) {
                    foreach ($customfields->attributes['employee']['label'] as $key => $label) {
                        $val = isset($emp->custom_values[$key]) ? $emp->custom_values[$key] : '';
                        echo '<td>' . gp_escape_html($val) . '</td>';
                    }
                }
                ?>
            </tr>
            <?php endforeach; ?>
            <?php if (empty($employees)): ?>
            <tr><td colspan="7">No employees found.</td></tr>
            <?php endif; ?>
        </tbody>
    </table>
</div>
<?php
gp_page_footer();
