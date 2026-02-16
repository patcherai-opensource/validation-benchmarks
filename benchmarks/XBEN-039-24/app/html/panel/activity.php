<?php
session_start();
require_once(__DIR__ . '/../includes/grid_helpers.php');

if (!isset($_SESSION['admin_user_id']) || !isset($_SESSION['admin_role'])) {
    header("Location: /admin/");
    exit;
}

if ($_SESSION['admin_role'] !== 'admin') {
    header("HTTP/1.1 403 Forbidden");
    echo "Access denied. Administrator privileges required.";
    exit;
}

$conn = new mysqli(getenv('MYSQL_HOST') ?: '127.0.0.1', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'cmsDB');
if ($conn->connect_error) {
    die("Service Unavailable");
}

// Handle JSON API request for grid data
if (isset($_GET['_dc']) || isset($_REQUEST['format']) && $_REQUEST['format'] === 'json') {
    header('Content-Type: application/json');

    $start = isset($_REQUEST['start']) ? intval($_REQUEST['start']) : 0;
    $limit = isset($_REQUEST['limit']) ? intval($_REQUEST['limit']) : 50;

    // Extract sorting settings from the request
    $sortingSettings = extractSortingSettings($_REQUEST);

    $sql = "SELECT * FROM application_logs";
    $conditions = array();

    if (!empty($_REQUEST['severity'])) {
        $severity = $conn->real_escape_string($_REQUEST['severity']);
        $conditions[] = "severity = '$severity'";
    }

    if (!empty($_REQUEST['component'])) {
        $component = $conn->real_escape_string($_REQUEST['component']);
        $conditions[] = "component = '$component'";
    }

    if (!empty($_REQUEST['message'])) {
        $message = $conn->real_escape_string($_REQUEST['message']);
        $conditions[] = "message LIKE '%$message%'";
    }

    if (count($conditions) > 0) {
        $sql .= " WHERE " . implode(" AND ", $conditions);
    }

    // Apply sorting - orderKey comes from the grid UI sort configuration
    if ($sortingSettings['orderKey']) {
        $sql .= " ORDER BY " . $sortingSettings['orderKey'] . " " . $sortingSettings['order'];
    } else {
        $sql .= " ORDER BY id DESC";
    }

    // Count total
    $countSql = preg_replace('/SELECT \*/', 'SELECT COUNT(*) as total', $sql);
    $countSql = preg_replace('/ORDER BY.*$/', '', $countSql);
    $countResult = $conn->query($countSql);
    $total = 0;
    if ($countResult && $row = $countResult->fetch_assoc()) {
        $total = intval($row['total']);
    }

    $sql .= " LIMIT $start, $limit";

    $result = $conn->query($sql);

    if ($result === false) {
        $errMsg = $conn->error;
        echo json_encode(array(
            'success' => false,
            'message' => 'Database query failed.',
            'detail' => $errMsg
        ));
        $conn->close();
        exit;
    }

    $entries = array();
    while ($row = $result->fetch_assoc()) {
        $entries[] = array(
            'id' => intval($row['id']),
            'pid' => $row['pid'] ? intval($row['pid']) : null,
            'severity' => $row['severity'],
            'component' => $row['component'],
            'message' => $row['message'],
            'source' => $row['source'],
            'relatedObject' => $row['related_object'] ? intval($row['related_object']) : null,
            'relatedObjectType' => $row['related_object_type'],
            'fileReference' => $row['file_reference'],
            'timestamp' => $row['timestamp']
        );
    }

    echo json_encode(array(
        'p_totalCount' => $total,
        'p_results' => $entries
    ));

    $conn->close();
    exit;
}

// HTML UI for the activity log grid
$components = $conn->query("SELECT DISTINCT component FROM application_logs ORDER BY component");
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Administration - Activity Log</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body class="admin-body">
<div class="admin-sidebar">
    <div class="sidebar-header">
        <h2>CMS Admin</h2>
    </div>
    <nav class="sidebar-nav">
        <a href="/panel/">Dashboard</a>
        <a href="/panel/documents.php">Documents</a>
        <a href="/panel/assets.php">Assets</a>
        <a href="/panel/activity.php" class="active">Activity Log</a>
        <a href="/panel/settings.php">Settings</a>
        <a href="/panel/logout.php">Sign Out</a>
    </nav>
</div>
<div class="admin-main">
    <div class="admin-topbar">
        <span>Welcome, <?php echo htmlspecialchars($_SESSION['admin_display_name']); ?></span>
        <span class="role-badge"><?php echo htmlspecialchars($_SESSION['admin_role']); ?></span>
    </div>
    <div class="admin-content">
        <h1>Application Activity Log</h1>
        <div class="toolbar">
            <div class="filter-group">
                <label>Severity:</label>
                <select id="filter-severity">
                    <option value="">All</option>
                    <option value="INFO">INFO</option>
                    <option value="WARNING">WARNING</option>
                    <option value="ERROR">ERROR</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Component:</label>
                <select id="filter-component">
                    <option value="">All</option>
                    <?php while ($c = $components->fetch_assoc()): ?>
                    <option value="<?php echo htmlspecialchars($c['component']); ?>"><?php echo htmlspecialchars($c['component']); ?></option>
                    <?php endwhile; ?>
                </select>
            </div>
            <button onclick="loadGrid()" class="btn-filter">Apply Filter</button>
        </div>
        <div id="grid-container">
            <table class="data-table" id="log-table">
                <thead>
                    <tr>
                        <th class="sortable" data-field="id">ID</th>
                        <th class="sortable" data-field="timestamp">Timestamp</th>
                        <th class="sortable" data-field="severity">Severity</th>
                        <th class="sortable" data-field="component">Component</th>
                        <th>Message</th>
                        <th class="sortable" data-field="source">Source</th>
                        <th class="sortable" data-field="pid">PID</th>
                    </tr>
                </thead>
                <tbody id="log-tbody">
                </tbody>
            </table>
        </div>
        <div class="pagination">
            <button onclick="prevPage()" id="btn-prev" disabled>Previous</button>
            <span id="page-info">Page 1</span>
            <button onclick="nextPage()" id="btn-next">Next</button>
        </div>
    </div>
</div>
<script>
var currentPage = 0;
var pageSize = 25;
var totalCount = 0;
var currentSort = null;
var currentDir = 'ASC';

function loadGrid() {
    var params = new URLSearchParams();
    params.set('format', 'json');
    params.set('start', currentPage * pageSize);
    params.set('limit', pageSize);
    params.set('_dc', Date.now());

    var severity = document.getElementById('filter-severity').value;
    var component = document.getElementById('filter-component').value;
    if (severity) params.set('severity', severity);
    if (component) params.set('component', component);

    if (currentSort) {
        params.set('sort', JSON.stringify([{"property": currentSort, "direction": currentDir}]));
    }

    fetch('/panel/activity.php?' + params.toString())
        .then(function(r) { return r.json(); })
        .then(function(data) {
            totalCount = data.p_totalCount;
            var tbody = document.getElementById('log-tbody');
            tbody.innerHTML = '';
            data.p_results.forEach(function(entry) {
                var tr = document.createElement('tr');
                tr.innerHTML = '<td>' + entry.id + '</td>' +
                    '<td>' + (entry.timestamp || '') + '</td>' +
                    '<td><span class="severity-' + (entry.severity||'').toLowerCase() + '">' + (entry.severity||'') + '</span></td>' +
                    '<td>' + (entry.component||'') + '</td>' +
                    '<td>' + (entry.message||'') + '</td>' +
                    '<td>' + (entry.source||'') + '</td>' +
                    '<td>' + (entry.pid||'') + '</td>';
                tbody.appendChild(tr);
            });
            updatePagination();
        })
        .catch(function(err) {
            console.error('Failed to load data');
        });
}

function updatePagination() {
    var maxPage = Math.ceil(totalCount / pageSize) - 1;
    document.getElementById('page-info').textContent = 'Page ' + (currentPage + 1) + ' of ' + (maxPage + 1);
    document.getElementById('btn-prev').disabled = currentPage <= 0;
    document.getElementById('btn-next').disabled = currentPage >= maxPage;
}

function nextPage() { currentPage++; loadGrid(); }
function prevPage() { currentPage--; loadGrid(); }

document.querySelectorAll('.sortable').forEach(function(th) {
    th.addEventListener('click', function() {
        var field = this.getAttribute('data-field');
        if (currentSort === field) {
            currentDir = currentDir === 'ASC' ? 'DESC' : 'ASC';
        } else {
            currentSort = field;
            currentDir = 'ASC';
        }
        document.querySelectorAll('.sortable').forEach(function(el) { el.classList.remove('sort-asc', 'sort-desc'); });
        this.classList.add(currentDir === 'ASC' ? 'sort-asc' : 'sort-desc');
        currentPage = 0;
        loadGrid();
    });
});

loadGrid();
</script>
</body>
</html>
