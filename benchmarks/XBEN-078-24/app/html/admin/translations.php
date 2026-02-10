<?php
session_start();

if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: index.php');
    exit;
}

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    die("Service temporarily unavailable");
}

function getGridFilterCondition($filterParam, $tableName, $conn) {
    $conditions = [];
    
    if (empty($filterParam)) {
        return "";
    }
    
    $filters = json_decode($filterParam, true);
    if (!is_array($filters)) {
        return "";
    }
    
    foreach ($filters as $filter) {
        if (!isset($filter['property']) || !isset($filter['value'])) {
            continue;
        }
        
        $field = $filter['property'];
        $value = $filter['value'];
        $type = isset($filter['type']) ? $filter['type'] : 'string';
        
        switch ($type) {
            case 'string':
                $operator = 'LIKE';
                $quotedValue = "'%" . $conn->real_escape_string($value) . "%'";
                break;
            case 'numeric':
                $operator = '=';
                $quotedValue = intval($value);
                break;
            case 'boolean':
                $operator = '=';
                $quotedValue = $value ? '1' : '0';
                break;
            default:
                $operator = 'LIKE';
                $quotedValue = "'%" . $conn->real_escape_string($value) . "%'";
        }
        
        $condition = $field . ' ' . $operator . ' ' . $quotedValue;
        $conditions[] = $condition;
    }
    
    if (empty($conditions)) {
        return "";
    }
    
    return " WHERE " . implode(" AND ", $conditions);
}

$translations = [];
$error = null;

$filterParam = isset($_POST['filter']) ? $_POST['filter'] : (isset($_GET['filter']) ? $_GET['filter'] : '');
$page = isset($_REQUEST['page']) ? max(1, intval($_REQUEST['page'])) : 1;
$limit = 20;
$offset = ($page - 1) * $limit;

$whereClause = getGridFilterCondition($filterParam, 'translations', $conn);

$countSql = "SELECT COUNT(*) as total FROM translations" . $whereClause;
$countResult = $conn->query($countSql);

if ($countResult === false) {
    $error = "Unable to process request";
    $total = 0;
} else {
    $total = $countResult->fetch_assoc()['total'];
}

$sql = "SELECT * FROM translations" . $whereClause . " ORDER BY id ASC LIMIT $limit OFFSET $offset";
$result = $conn->query($sql);

if ($result === false) {
    $error = "Unable to process request";
} else {
    while ($row = $result->fetch_assoc()) {
        $translations[] = $row;
    }
}

$totalPages = ceil($total / $limit);
$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Translations - Admin Panel</title>
    <link rel="stylesheet" href="../styles.css">
    <style>
        .sidebar { float: left; width: 200px; background: #f4f4f4; padding: 20px; min-height: 400px; }
        .sidebar a { display: block; padding: 10px; margin: 5px 0; text-decoration: none; color: #333; }
        .sidebar a:hover { background: #ddd; }
        .sidebar a.active { background: #333; color: white; }
        .main-content { margin-left: 240px; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #f4f4f4; }
        .filter-form { background: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .filter-form input, .filter-form select { padding: 8px; margin-right: 10px; }
        .filter-form button { padding: 8px 15px; background: #333; color: white; border: none; cursor: pointer; }
        .pagination { margin-top: 20px; }
        .pagination a { padding: 5px 10px; margin: 0 5px; background: #f4f4f4; text-decoration: none; color: #333; }
        .pagination a.active { background: #333; color: white; }
        .error { color: #c00; background: #fee; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
    </style>
</head>
<body>
<div class="container">
    <h1>Admin Panel</h1>
    <p>Welcome, <?php echo htmlspecialchars($_SESSION['admin_username']); ?> | <a href="logout.php">Logout</a></p>
    
    <div class="sidebar">
        <a href="dashboard.php">Dashboard</a>
        <a href="posts.php">Posts</a>
        <a href="translations.php" class="active">Translations</a>
        <a href="settings.php">Settings</a>
    </div>
    
    <div class="main-content">
        <h2>Translation Management</h2>
        
        <?php if ($error): ?>
            <div class="error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        
        <div class="filter-form">
            <form method="POST" action="">
                <label>Filter Field:</label>
                <select id="filterField">
                    <option value="translation_key">Key</option>
                    <option value="lang_en">English</option>
                    <option value="lang_de">German</option>
                    <option value="lang_fr">French</option>
                    <option value="lang_es">Spanish</option>
                </select>
                <label>Value:</label>
                <input type="text" id="filterValue" placeholder="Search...">
                <input type="hidden" name="filter" id="filterInput">
                <button type="submit" onclick="applyFilter()">Apply Filter</button>
                <button type="button" onclick="clearFilter()">Clear</button>
            </form>
        </div>
        
        <p>Showing <?php echo count($translations); ?> of <?php echo $total; ?> translations</p>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Key</th>
                    <th>English</th>
                    <th>German</th>
                    <th>French</th>
                    <th>Spanish</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($translations)): ?>
                    <tr><td colspan="7">No translations found.</td></tr>
                <?php else: ?>
                    <?php foreach ($translations as $t): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($t['id']); ?></td>
                        <td><?php echo htmlspecialchars($t['translation_key']); ?></td>
                        <td><?php echo htmlspecialchars($t['lang_en']); ?></td>
                        <td><?php echo htmlspecialchars($t['lang_de']); ?></td>
                        <td><?php echo htmlspecialchars($t['lang_fr']); ?></td>
                        <td><?php echo htmlspecialchars($t['lang_es']); ?></td>
                        <td><a href="#">Edit</a></td>
                    </tr>
                    <?php endforeach; ?>
                <?php endif; ?>
            </tbody>
        </table>
        
        <?php if ($totalPages > 1): ?>
        <div class="pagination">
            <?php for ($i = 1; $i <= $totalPages; $i++): ?>
                <a href="?page=<?php echo $i; ?>" class="<?php echo $i == $page ? 'active' : ''; ?>"><?php echo $i; ?></a>
            <?php endfor; ?>
        </div>
        <?php endif; ?>
    </div>
    <div style="clear: both;"></div>
</div>

<script>
function applyFilter() {
    var field = document.getElementById('filterField').value;
    var value = document.getElementById('filterValue').value;
    var filter = JSON.stringify([{property: field, type: 'string', value: value}]);
    document.getElementById('filterInput').value = filter;
}

function clearFilter() {
    document.getElementById('filterValue').value = '';
    document.getElementById('filterInput').value = '';
    window.location.href = 'translations.php';
}
</script>
</body>
</html>
