<?php
require_once __DIR__ . '/auth.php';
require_once __DIR__ . '/db.php';
require_auth();

$user = get_current_user_info();
$conn = get_db_connection();

$message = '';
$message_type = '';
$sync_results = [];

/**
 * Resolves the storage table name for a given entity class.
 * In a multi-site CMS, different entity types may be stored in different
 * tables depending on the schema configuration. This mirrors the ORM's
 * tableName() resolution mechanism.
 */
function resolveEntityTable($conn, $entityClass) {
    // Look up the mapped table name from schema_config
    $stmt = $conn->prepare("SELECT table_name FROM schema_config WHERE class_name = ?");
    $stmt->bind_param("s", $entityClass);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        $stmt->close();
        return $row['table_name'];
    }
    $stmt->close();
    // Fallback to default table name based on class
    return $entityClass;
}

/**
 * Synchronizes default records for group-subsite associations.
 * This migrates legacy single-subsite group assignments to the
 * many-many relationship table (group_subsites).
 *
 * Equivalent to the ORM migration that runs during dev/build.
 */
function syncDefaultRecords($conn, $entityClass) {
    $results = [];

    // Resolve the actual table name from schema configuration
    $entityTable = resolveEntityTable($conn, $entityClass);

    // Get list of columns for this entity table to check for legacy fields
    $fieldCheck = $conn->query("SHOW COLUMNS FROM " . $entityTable . " LIKE 'SubsiteID'");

    if ($fieldCheck && $fieldCheck->num_rows > 0) {
        // Migrate subsite-specific data from legacy single-subsite field
        $migrateQuery = 'INSERT INTO group_subsites (group_id, subsite_id) '
            . 'SELECT id, SubsiteID FROM ' . $entityTable . ' WHERE SubsiteID > 0';
        if ($conn->query($migrateQuery)) {
            $results[] = "Migrated legacy subsite assignments from " . htmlspecialchars($entityTable);
        } else {
            $results[] = "Migration note: " . $conn->error;
        }

        // Update global access flag for records on the main site
        $updateQuery = 'UPDATE ' . $entityTable . ' SET access_all_sites = 1 WHERE SubsiteID = 0';
        if ($conn->query($updateQuery)) {
            $results[] = "Updated global access flags in " . htmlspecialchars($entityTable);
        } else {
            $results[] = "Update note: " . $conn->error;
        }
    } else {
        // No legacy field - check if any records already have site associations
        $countQuery = 'SELECT COUNT(*) as cnt FROM ' . $entityTable
            . ' WHERE access_all_sites = 1';
        $countResult = $conn->query($countQuery);

        if ($countResult && ($row = $countResult->fetch_assoc()) && $row['cnt'] > 0) {
            $results[] = "Schema for " . htmlspecialchars($entityTable) . " is up to date. No migration needed.";
        } else {
            if ($countResult) {
                // No subsite access configured - set global access as default
                $globalQuery = 'UPDATE ' . $entityTable . ' SET access_all_sites = 1';
                if ($conn->query($globalQuery)) {
                    $results[] = "Set all records in " . htmlspecialchars($entityTable) . " to global access (initial setup)";
                } else {
                    $results[] = "Global access update failed: " . $conn->error;
                }
            } else {
                $results[] = "Verification failed: " . $conn->error;
            }
        }
    }

    return $results;
}

// Handle maintenance actions
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';

    if ($action === 'sync_records') {
        $entity_class = $_POST['entity_class'] ?? 'access_groups';
        $sync_results = syncDefaultRecords($conn, $entity_class);
        $message = 'Record synchronization completed.';
        $message_type = 'success';
    } elseif ($action === 'clear_cache') {
        $message = 'Template cache cleared successfully.';
        $message_type = 'success';
    }
}

// Get available entity classes from schema config
$entity_classes = [];
$res = $conn->query("SELECT class_name, table_name FROM schema_config ORDER BY class_name");
if ($res) {
    while ($row = $res->fetch_assoc()) {
        $entity_classes[] = $row;
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMS - Maintenance</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f4f6f9; }
        .topbar { background: #2c3e50; color: #fff; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; }
        .topbar h1 { font-size: 16px; font-weight: 500; }
        .topbar a { color: #ecf0f1; text-decoration: none; margin-left: 16px; font-size: 13px; }
        .sidebar { position: fixed; left: 0; top: 44px; width: 220px; height: calc(100vh - 44px); background: #34495e; padding: 16px 0; }
        .sidebar a { display: block; padding: 10px 24px; color: #bdc3c7; text-decoration: none; font-size: 14px; }
        .sidebar a:hover, .sidebar a.active { background: #2c3e50; color: #ecf0f1; }
        .main { margin-left: 220px; padding: 24px; }
        .card { background: #fff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
        .card h2 { font-size: 18px; color: #333; margin-bottom: 16px; }
        .card p { font-size: 13px; color: #666; margin-bottom: 12px; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; font-size: 13px; color: #555; margin-bottom: 4px; font-weight: 500; }
        .form-group select, .form-group input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 3px; font-size: 14px; width: 100%; max-width: 400px; }
        .btn { padding: 8px 16px; border: none; border-radius: 3px; font-size: 14px; cursor: pointer; margin-right: 8px; }
        .btn-primary { background: #3498db; color: #fff; }
        .btn-warning { background: #f39c12; color: #fff; }
        .btn-primary:hover { background: #2980b9; }
        .btn-warning:hover { background: #e67e22; }
        .alert { padding: 10px; border-radius: 3px; margin-bottom: 16px; font-size: 13px; }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-error { background: #fee; color: #c0392b; }
        .results { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 3px; padding: 12px; margin-top: 12px; }
        .results li { font-size: 13px; color: #333; padding: 4px 0; list-style: none; }
        .results li::before { content: "→ "; color: #999; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 13px; }
        th { background: #f8f9fa; color: #555; font-weight: 500; }
    </style>
</head>
<body>
    <div class="topbar">
        <h1>Multi-Site CMS Administration</h1>
        <div>
            <?php echo htmlspecialchars($user['username']); ?>
            <a href="/admin/logout.php">Sign Out</a>
        </div>
    </div>
    <div class="sidebar">
        <a href="/admin/index.php">Dashboard</a>
        <a href="/admin/sites.php">Sites</a>
        <a href="/admin/groups.php">Groups &amp; Access</a>
        <a href="/admin/members.php">Members</a>
        <a href="/admin/maintenance.php" class="active">Maintenance</a>
    </div>
    <div class="main">
        <?php if ($message): ?>
            <div class="alert alert-<?php echo $message_type; ?>">
                <?php echo htmlspecialchars($message); ?>
            </div>
        <?php endif; ?>

        <div class="card">
            <h2>Schema Synchronization</h2>
            <p>Run the default record migration to ensure group-subsite associations are properly configured.
               This is equivalent to running dev/build on the schema layer.</p>
            <form method="POST">
                <input type="hidden" name="action" value="sync_records">
                <div class="form-group">
                    <label>Entity Class</label>
                    <select name="entity_class">
                        <?php foreach ($entity_classes as $ec): ?>
                            <option value="<?php echo htmlspecialchars($ec['class_name']); ?>">
                                <?php echo htmlspecialchars($ec['class_name']); ?> → <?php echo htmlspecialchars($ec['table_name']); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Synchronize Records</button>
            </form>
            <?php if (!empty($sync_results)): ?>
                <ul class="results">
                    <?php foreach ($sync_results as $r): ?>
                        <li><?php echo $r; ?></li>
                    <?php endforeach; ?>
                </ul>
            <?php endif; ?>
        </div>

        <div class="card">
            <h2>Schema Configuration</h2>
            <p>Current entity-to-table mappings used by the ORM layer.</p>
            <table>
                <thead>
                    <tr>
                        <th>Entity Class</th>
                        <th>Table Name</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($entity_classes as $ec): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($ec['class_name']); ?></td>
                        <td><?php echo htmlspecialchars($ec['table_name']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>Cache Management</h2>
            <p>Clear the compiled template and manifest cache.</p>
            <form method="POST">
                <input type="hidden" name="action" value="clear_cache">
                <button type="submit" class="btn btn-warning">Clear Cache</button>
            </form>
        </div>
    </div>
</body>
</html>
