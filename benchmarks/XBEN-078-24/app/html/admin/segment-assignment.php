<?php
require_once __DIR__ . '/auth.php';
requireAdmin();

$conn = getDbConnection();
$action = $_GET['action'] ?? '';

if ($action === 'inheritable-segments') {
    header('Content-Type: application/json');

    $id = $_GET['id'] ?? '';
    $type = $_GET['type'] ?? '';

    if (empty($id) || empty($type)) {
        echo json_encode(['success' => false, 'message' => 'Missing required parameters.']);
        exit;
    }

    // Build parent lookup query based on element type
    $escapedId = $conn->real_escape_string($id);
    $parentIdStatement = sprintf(
        "SELECT `%s` FROM `%s` WHERE `%s` = '%s'",
        $type === 'object' ? 'o_parentId' : 'parentId',
        $type . 's',
        $type === 'object' ? 'o_id' : 'id',
        $escapedId
    );

    $queryResult = $conn->query($parentIdStatement);
    if ($queryResult === false) {
        echo json_encode(['success' => true, 'data' => ['segments' => [], 'elementId' => $id, 'elementType' => $type]]);
        $conn->close();
        exit;
    }
    $parentRow = $queryResult->fetch_assoc();

    if (!$parentRow) {
        echo json_encode(['success' => true, 'data' => ['segments' => [], 'elementId' => $id, 'elementType' => $type]]);
        $conn->close();
        exit;
    }

    $parentId = array_values($parentRow)[0] ?? 0;

    // Collect inheritable segments walking up the parent chain
    $segments = [];
    $currentId = (int)$parentId;
    $depth = 0;
    $maxDepth = 10;

    while ($currentId > 0 && $depth < $maxDepth) {
        $segStmt = $conn->prepare(
            "SELECT sa.segmentId, cs.name, cs.`group`, sa.breaksInheritance
             FROM plugin_cmf_segment_assignment sa
             LEFT JOIN plugin_cmf_customer_segments cs ON sa.segmentId = cs.id
             WHERE sa.elementId = ? AND sa.elementType = ?"
        );
        $safeType = $type === 'object' ? 'object' : (($type === 'document') ? 'document' : 'asset');
        $segStmt->bind_param("is", $currentId, $safeType);
        $segStmt->execute();
        $segResult = $segStmt->get_result();

        while ($row = $segResult->fetch_assoc()) {
            if ($row['breaksInheritance']) {
                break 2;
            }
            $segments[] = [
                'segmentId' => (int)$row['segmentId'],
                'name' => $row['name'],
                'group' => $row['group'],
                'inheritedFrom' => $currentId,
                'depth' => $depth
            ];
        }
        $segStmt->close();

        // Walk to next parent using safe query
        $nextStmt = $conn->prepare(
            "SELECT o_parentId FROM objects WHERE o_id = ?"
        );
        $nextStmt->bind_param("i", $currentId);
        $nextStmt->execute();
        $nextResult = $nextStmt->get_result();
        $nextRow = $nextResult->fetch_assoc();
        $currentId = $nextRow ? ((int)($nextRow['o_parentId'] ?? 0)) : 0;
        $nextStmt->close();

        $depth++;
    }

    echo json_encode([
        'success' => true,
        'data' => [
            'segments' => $segments,
            'elementId' => $id,
            'elementType' => $type,
            'parentId' => $parentId
        ]
    ]);
    $conn->close();
    exit;
}

if ($action === 'list') {
    header('Content-Type: application/json');

    $elementType = $_GET['elementType'] ?? 'object';
    $page = max(1, (int)($_GET['page'] ?? 1));
    $limit = min(50, max(1, (int)($_GET['limit'] ?? 20)));
    $offset = ($page - 1) * $limit;

    $stmt = $conn->prepare(
        "SELECT sa.elementId, sa.elementType, sa.segmentId, sa.breaksInheritance, cs.name as segmentName
         FROM plugin_cmf_segment_assignment sa
         LEFT JOIN plugin_cmf_customer_segments cs ON sa.segmentId = cs.id
         WHERE sa.elementType = ?
         LIMIT ? OFFSET ?"
    );
    $stmt->bind_param("sii", $elementType, $limit, $offset);
    $stmt->execute();
    $result = $stmt->get_result();

    $assignments = [];
    while ($row = $result->fetch_assoc()) {
        $assignments[] = $row;
    }

    echo json_encode(['success' => true, 'data' => $assignments]);
    $stmt->close();
    $conn->close();
    exit;
}

// Default: show segment assignment management page
$assignments = [];
$assignResult = $conn->query(
    "SELECT sa.elementId, sa.elementType, sa.segmentId, sa.breaksInheritance, cs.name as segmentName, cs.`group` as segmentGroup
     FROM plugin_cmf_segment_assignment sa
     LEFT JOIN plugin_cmf_customer_segments cs ON sa.segmentId = cs.id
     ORDER BY sa.elementType, sa.elementId"
);
if ($assignResult) {
    while ($row = $assignResult->fetch_assoc()) {
        $assignments[] = $row;
    }
}
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore Admin - Segment Assignments</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>pimcore</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="/admin/dashboard.php">Dashboard</a></li>
                <li><a href="/admin/customers.php">Customers</a></li>
                <li><a href="/admin/segments.php">Segments</a></li>
                <li class="active"><a href="/admin/segment-assignment.php">Segment Assignments</a></li>
                <li><a href="/admin/objects.php">Data Objects</a></li>
                <li><a href="/admin/documents.php">Documents</a></li>
                <li><a href="/admin/assets.php">Assets</a></li>
                <li class="nav-divider"></li>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header">
                <h1>Customer Segment Assignments</h1>
                <span class="user-info">Logged in as: <?php echo htmlspecialchars($_SESSION['pimcore_user']); ?></span>
            </div>

            <div class="toolbar">
                <h3>Inheritance Lookup</h3>
                <form method="GET" action="/admin/segment-assignment.php" class="inline-form">
                    <input type="hidden" name="action" value="inheritable-segments">
                    <label for="type">Element Type:</label>
                    <select name="type" id="type">
                        <option value="object">Object</option>
                        <option value="document">Document</option>
                        <option value="asset">Asset</option>
                    </select>
                    <label for="id">Element ID:</label>
                    <input type="text" name="id" id="id" placeholder="Enter element ID" size="10">
                    <button type="submit" class="btn">Lookup Inherited Segments</button>
                </form>
            </div>

            <div class="data-table-wrapper">
                <h3>Current Assignments</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Element ID</th>
                            <th>Element Type</th>
                            <th>Segment</th>
                            <th>Group</th>
                            <th>Breaks Inheritance</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($assignments as $a): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($a['elementId']); ?></td>
                            <td><?php echo htmlspecialchars($a['elementType']); ?></td>
                            <td><?php echo htmlspecialchars($a['segmentName'] ?? 'Unknown'); ?></td>
                            <td><?php echo htmlspecialchars($a['segmentGroup'] ?? '-'); ?></td>
                            <td><?php echo $a['breaksInheritance'] ? 'Yes' : 'No'; ?></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </main>
    </div>
</body>
</html>
