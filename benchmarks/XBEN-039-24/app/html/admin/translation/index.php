<?php
require_once __DIR__ . '/../config.php';
session_start();
check_admin_auth();

$conn = get_db();

$language = isset($_REQUEST['language']) ? $conn->real_escape_string($_REQUEST['language']) : '';
$filterKey = isset($_REQUEST['key']) ? $conn->real_escape_string($_REQUEST['key']) : '';

$sortingSettings = extract_sorting_settings($_REQUEST);

$conditions = [];
if (!empty($language)) {
    $conditions[] = "language = '" . $language . "'";
}
if (!empty($filterKey)) {
    $conditions[] = "`key` LIKE '%" . $filterKey . "%'";
}

$whereClause = '';
if (count($conditions) > 0) {
    $whereClause = 'WHERE ' . implode(' AND ', $conditions);
}

$sql = "SELECT `key`, language, text, type, creationDate, modificationDate FROM translations_admin " . $whereClause;

if (isset($sortingSettings['orderKey'])) {
    $order = isset($sortingSettings['order']) ? $sortingSettings['order'] : 'ASC';
    $sql .= " ORDER BY `" . $conn->real_escape_string($sortingSettings['orderKey']) . "` " . $order;
} else {
    $sql .= " ORDER BY `key` ASC";
}

$sql .= " LIMIT 50";

$result = $conn->query($sql);

if (is_api_request() || isset($_REQUEST['_dc'])) {
    $data = [];
    if ($result) {
        while ($row = $result->fetch_assoc()) {
            $data[] = $row;
        }
    }
    json_response(['success' => true, 'data' => $data]);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore Admin - Translations</title>
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
            <a href="/admin/" class="nav-item"><span class="nav-icon">&#9635;</span> Dashboard</a>
            <a href="/admin/log/show" class="nav-item"><span class="nav-icon">&#9776;</span> Application Logger</a>
            <a href="/admin/translation/" class="nav-item active"><span class="nav-icon">&#127760;</span> Translations</a>
            <a href="/admin/search/" class="nav-item"><span class="nav-icon">&#128269;</span> Search</a>
            <a href="/admin/asset/list" class="nav-item"><span class="nav-icon">&#128194;</span> Assets</a>
            <a href="/admin/document/list" class="nav-item"><span class="nav-icon">&#128196;</span> Documents</a>
        </nav>
        <div class="sidebar-footer">
            <span class="user-info"><?php echo htmlspecialchars($_SESSION['pimcore_admin_name']); ?></span>
            <a href="/admin/logout.php" class="logout-link">Logout</a>
        </div>
    </div>
    <div class="admin-content">
        <div class="content-header">
            <h1>Admin Translations</h1>
            <div class="toolbar">
                <form method="GET" action="/admin/translation/" class="filter-form">
                    <select name="language" class="form-control">
                        <option value="">All Languages</option>
                        <option value="en" <?php echo $language === 'en' ? 'selected' : ''; ?>>English</option>
                        <option value="de" <?php echo $language === 'de' ? 'selected' : ''; ?>>Deutsch</option>
                    </select>
                    <input type="text" name="key" class="form-control" placeholder="Search key..." value="<?php echo htmlspecialchars($filterKey); ?>">
                    <button type="submit" class="btn btn-secondary">Filter</button>
                </form>
            </div>
        </div>
        <table class="data-table">
            <thead>
                <tr><th>Key</th><th>Language</th><th>Text</th><th>Type</th></tr>
            </thead>
            <tbody>
            <?php
            if ($result) {
                while ($row = $result->fetch_assoc()) {
                    echo "<tr>";
                    echo "<td>" . htmlspecialchars($row['key']) . "</td>";
                    echo "<td>" . htmlspecialchars($row['language']) . "</td>";
                    echo "<td>" . htmlspecialchars($row['text']) . "</td>";
                    echo "<td>" . htmlspecialchars($row['type']) . "</td>";
                    echo "</tr>";
                }
            }
            ?>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
