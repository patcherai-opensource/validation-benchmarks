<?php
/**
 * Dashboard / Home page
 */
$db = get_db();
$user = get_current_user_info();

// Get counts
$emp_count = $db->query("SELECT COUNT(*) FROM gp_employees WHERE status = 1")->fetchColumn();
$proj_count = $db->query("SELECT COUNT(*) FROM gp_projects WHERE status = 1")->fetchColumn();
$dept_count = $db->query("SELECT COUNT(DISTINCT department) FROM gp_employees")->fetchColumn();

gp_page_header('Dashboard');
?>
<div class="gp-content">
    <h2>Dashboard</h2>
    <p>Welcome back, <?php echo gp_escape_html($user['name']); ?>.</p>

    <div class="gp-dashboard-cards">
        <div class="gp-card">
            <div class="gp-card-number"><?php echo intval($emp_count); ?></div>
            <div class="gp-card-label">Active Employees</div>
            <a href="/index.php?module=employee&action=list">View all &raquo;</a>
        </div>
        <div class="gp-card">
            <div class="gp-card-number"><?php echo intval($proj_count); ?></div>
            <div class="gp-card-label">Active Projects</div>
            <a href="/index.php?module=project&action=list">View all &raquo;</a>
        </div>
        <div class="gp-card">
            <div class="gp-card-number"><?php echo intval($dept_count); ?></div>
            <div class="gp-card-label">Departments</div>
        </div>
    </div>

    <?php if ($user['admin']): ?>
    <div class="gp-admin-notice">
        <h3>Administration</h3>
        <p>You are logged in as an administrator. Access the <a href="/index.php?module=admin&page=modules">Administration panel</a> to manage modules and settings.</p>
    </div>
    <?php endif; ?>
</div>
<?php
gp_page_footer();
