<?php
require_once __DIR__ . '/../config.php';
session_start();
check_admin_auth();

$conn = get_db();

$page = isset($_REQUEST['page']) ? max(1, (int)$_REQUEST['page']) : 1;
$start = isset($_REQUEST['start']) ? max(0, (int)$_REQUEST['start']) : 0;
$limit = isset($_REQUEST['limit']) ? min(100, max(1, (int)$_REQUEST['limit'])) : 25;

$filterPriority = isset($_REQUEST['priority']) ? $conn->real_escape_string($_REQUEST['priority']) : '';
$filterComponent = isset($_REQUEST['component']) ? $conn->real_escape_string($_REQUEST['component']) : '';
$filterMessage = isset($_REQUEST['message']) ? $conn->real_escape_string($_REQUEST['message']) : '';

$sortingSettings = extract_sorting_settings($_REQUEST);

$conditions = [];
if (!empty($filterPriority)) {
    $conditions[] = "priority = '" . $filterPriority . "'";
}
if (!empty($filterComponent)) {
    $conditions[] = "component LIKE '%" . $filterComponent . "%'";
}
if (!empty($filterMessage)) {
    $conditions[] = "message LIKE '%" . $filterMessage . "%'";
}

$whereClause = '';
if (count($conditions) > 0) {
    $whereClause = 'WHERE ' . implode(' AND ', $conditions);
}

$countSql = "SELECT COUNT(*) as total FROM application_logs " . $whereClause;
$countResult = $conn->query($countSql);
$total = $countResult ? $countResult->fetch_assoc()['total'] : 0;

$sql = "SELECT id, pid, timestamp, message, priority, component, source, fileobject, relatedobject, relatedobjecttype FROM application_logs " . $whereClause;

if (isset($sortingSettings['orderKey'])) {
    $order = isset($sortingSettings['order']) ? $sortingSettings['order'] : 'ASC';
    $sql .= " ORDER BY " . $sortingSettings['orderKey'] . " " . $order;
} else {
    $sql .= " ORDER BY id DESC";
}

$sql .= " LIMIT " . (int)$start . ", " . (int)$limit;

$result = $conn->query($sql);

if (is_api_request() || isset($_REQUEST['_dc'])) {
    $data = [];
    if ($result) {
        while ($row = $result->fetch_assoc()) {
            $data[] = $row;
        }
        json_response([
            'success' => true,
            'data' => $data,
            'total' => (int)$total
        ]);
    } else {
        json_response(['success' => false, 'message' => $conn->error], 500);
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore Admin - Application Logger</title>
    <link rel="stylesheet" href="/admin/static/pimcore.css">
</head>
<body>
<div class="admin-layout">
    <div class="admin-sidebar">
        <div class="sidebar-logo">
            <svg width="100" height="32" viewBox="0 0 100 32">
                <text x="0" y="24" font-family="Arial, sans-serif" font-size="22" font-weight="bold" fill="#fff">pimcore</text>
            </svg>
        </div>
        <nav class="sidebar-nav">
            <a href="/admin/" class="nav-item">
                <span class="nav-icon">&#9635;</span> Dashboard
            </a>
            <a href="/admin/log/show" class="nav-item active">
                <span class="nav-icon">&#9776;</span> Application Logger
            </a>
            <a href="/admin/translation/" class="nav-item">
                <span class="nav-icon">&#127760;</span> Translations
            </a>
            <a href="/admin/search/" class="nav-item">
                <span class="nav-icon">&#128269;</span> Search
            </a>
            <a href="/admin/asset/list" class="nav-item">
                <span class="nav-icon">&#128194;</span> Assets
            </a>
            <a href="/admin/document/list" class="nav-item">
                <span class="nav-icon">&#128196;</span> Documents
            </a>
        </nav>
        <div class="sidebar-footer">
            <span class="user-info"><?php echo htmlspecialchars($_SESSION['pimcore_admin_name']); ?></span>
            <a href="/admin/logout.php" class="logout-link">Logout</a>
        </div>
    </div>
    <div class="admin-content">
        <div class="content-header">
            <h1>Application Logger</h1>
            <div class="toolbar">
                <form method="GET" action="/admin/log/show" class="filter-form">
                    <select name="priority" class="form-control">
                        <option value="">All Priorities</option>
                        <?php foreach(['debug','info','warning','error','critical'] as $p): ?>
                        <option value="<?php echo $p; ?>" <?php echo $filterPriority === $p ? 'selected' : ''; ?>><?php echo ucfirst($p); ?></option>
                        <?php endforeach; ?>
                    </select>
                    <input type="text" name="component" class="form-control" placeholder="Component..." value="<?php echo htmlspecialchars($filterComponent); ?>">
                    <input type="text" name="message" class="form-control" placeholder="Search message..." value="<?php echo htmlspecialchars($filterMessage); ?>">
                    <button type="submit" class="btn btn-secondary">Filter</button>
                </form>
            </div>
        </div>
        <div class="log-table-container">
            <table class="data-table" id="logGrid">
                <thead>
                    <tr>
                        <th class="sortable" data-field="id">ID</th>
                        <th class="sortable" data-field="timestamp">Timestamp</th>
                        <th class="sortable" data-field="priority">Priority</th>
                        <th class="sortable" data-field="component">Component</th>
                        <th>Message</th>
                        <th class="sortable" data-field="source">Source</th>
                    </tr>
                </thead>
                <tbody>
                <?php
                $safeSql = "SELECT id, pid, timestamp, message, priority, component, source FROM application_logs " . $whereClause . " ORDER BY id DESC LIMIT " . (int)$start . ", " . (int)$limit;
                $r2 = $conn->query($safeSql);
                if ($r2) {
                    while ($row = $r2->fetch_assoc()) {
                        echo "<tr>";
                        echo "<td>" . htmlspecialchars($row['id']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['timestamp']) . "</td>";
                        echo "<td><span class='badge badge-" . htmlspecialchars($row['priority']) . "'>" . htmlspecialchars($row['priority']) . "</span></td>";
                        echo "<td>" . htmlspecialchars($row['component']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['message']) . "</td>";
                        echo "<td class='source-cell'>" . htmlspecialchars($row['source']) . "</td>";
                        echo "</tr>";
                    }
                }
                ?>
                </tbody>
            </table>
            <div class="pagination-info">
                Showing <?php echo $start + 1; ?> - <?php echo min($start + $limit, $total); ?> of <?php echo $total; ?> entries
            </div>
        </div>
        <script>
        document.querySelectorAll('.sortable').forEach(function(th) {
            th.addEventListener('click', function() {
                var field = this.dataset.field;
                var currentSort = new URLSearchParams(window.location.search).get('sort');
                var dir = 'ASC';
                if (currentSort) {
                    try {
                        var parsed = JSON.parse(currentSort);
                        if (parsed[0] && parsed[0].property === field && parsed[0].direction === 'ASC') {
                            dir = 'DESC';
                        }
                    } catch(e) {}
                }
                var params = new URLSearchParams(window.location.search);
                params.set('sort', JSON.stringify([{property: field, direction: dir}]));
                window.location.search = params.toString();
            });
            th.style.cursor = 'pointer';
        });
        </script>
    </div>
</div>
</body>
</html>
