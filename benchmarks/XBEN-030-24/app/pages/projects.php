<?php
/**
 * Projects list page
 */
$db = get_db();
$projects = $db->query("SELECT * FROM gp_projects ORDER BY title")->fetchAll();

gp_page_header('Projects');
?>
<div class="gp-content">
    <h2>Projects</h2>
    <table class="gp-table">
        <thead>
            <tr>
                <th>Ref</th>
                <th>Title</th>
                <th>Description</th>
                <th>Status</th>
                <th>Start Date</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($projects as $proj): ?>
            <tr>
                <td><?php echo gp_escape_html($proj['ref']); ?></td>
                <td><?php echo gp_escape_html($proj['title']); ?></td>
                <td><?php echo gp_escape_html($proj['description']); ?></td>
                <td><?php echo $proj['status'] ? 'Active' : 'Closed'; ?></td>
                <td><?php echo gp_escape_html($proj['dateo']); ?></td>
            </tr>
            <?php endforeach; ?>
            <?php if (empty($projects)): ?>
            <tr><td colspan="5">No projects found.</td></tr>
            <?php endif; ?>
        </tbody>
    </table>
</div>
<?php
gp_page_footer();
