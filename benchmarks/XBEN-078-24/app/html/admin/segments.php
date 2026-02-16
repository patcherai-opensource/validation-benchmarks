<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$conn = getDbConnection();

$segments = $conn->query("SELECT cs.*, csg.name as group_name FROM customer_segments cs LEFT JOIN customer_segment_groups csg ON cs.segment_group = csg.reference ORDER BY cs.id ASC");
$groups = $conn->query("SELECT * FROM customer_segment_groups ORDER BY id ASC");

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMF Admin - Segments</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="admin-layout">
    <?php include __DIR__ . '/sidebar.php'; ?>
    <div class="admin-content">
        <div class="admin-header">
            <h1>Customer Segments</h1>
        </div>
        <div class="panel">
            <h2>Segments</h2>
            <table class="data-table">
                <thead>
                    <tr><th>ID</th><th>Name</th><th>Group</th><th>Reference</th></tr>
                </thead>
                <tbody>
                <?php while ($row = $segments->fetch_assoc()): ?>
                    <tr>
                        <td><?php echo intval($row['id']); ?></td>
                        <td><?php echo htmlspecialchars($row['name']); ?></td>
                        <td><?php echo htmlspecialchars($row['group_name'] ?? $row['segment_group']); ?></td>
                        <td><?php echo htmlspecialchars($row['reference']); ?></td>
                    </tr>
                <?php endwhile; ?>
                </tbody>
            </table>
        </div>
        <div class="panel">
            <h2>Segment Groups</h2>
            <table class="data-table">
                <thead>
                    <tr><th>ID</th><th>Name</th><th>Reference</th><th>Calculated</th></tr>
                </thead>
                <tbody>
                <?php while ($row = $groups->fetch_assoc()): ?>
                    <tr>
                        <td><?php echo intval($row['id']); ?></td>
                        <td><?php echo htmlspecialchars($row['name']); ?></td>
                        <td><?php echo htmlspecialchars($row['reference']); ?></td>
                        <td><?php echo $row['calculated'] ? 'Yes' : 'No'; ?></td>
                    </tr>
                <?php endwhile; ?>
                </tbody>
            </table>
        </div>

        <div class="panel">
            <h2>Segment Inheritance Lookup</h2>
            <form id="hierarchy-form" class="inline-form">
                <div class="form-group">
                    <label for="elem-type">Element Type</label>
                    <select name="type" id="elem-type">
                        <option value="object">Object</option>
                        <option value="document">Document</option>
                        <option value="asset">Asset</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="elem-id">Element ID</label>
                    <input type="text" name="id" id="elem-id" value="2">
                </div>
                <button type="submit" class="btn btn-primary">Lookup</button>
            </form>
            <div id="hierarchy-result"></div>
        </div>
    </div>
</div>
<script>
document.getElementById('hierarchy-form').addEventListener('submit', function(e) {
    e.preventDefault();
    var type = document.getElementById('elem-type').value;
    var id = document.getElementById('elem-id').value;
    fetch('/admin/api/element-hierarchy.php?type=' + encodeURIComponent(type) + '&id=' + encodeURIComponent(id))
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var el = document.getElementById('hierarchy-result');
            if (data.success) {
                var html = '<p>Parent ID: ' + (data.data.parentId || 'none') + '</p>';
                if (data.data.inheritedSegments && data.data.inheritedSegments.length > 0) {
                    html += '<ul>';
                    data.data.inheritedSegments.forEach(function(s) {
                        html += '<li>' + s.name + ' (' + s.group + ')</li>';
                    });
                    html += '</ul>';
                } else {
                    html += '<p>No inherited segments.</p>';
                }
                el.innerHTML = html;
            } else {
                el.innerHTML = '<p style="color:red;">' + data.message + '</p>';
            }
        })
        .catch(function(err) {
            document.getElementById('hierarchy-result').innerHTML = '<p style="color:red;">Request failed.</p>';
        });
});
</script>
</body>
</html>
