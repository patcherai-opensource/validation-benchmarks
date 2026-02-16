<?php
require_once __DIR__ . '/../auth.php';
requireAuth();

$conn = getDbConnection();

$domain = isset($_GET['domain']) ? $_GET['domain'] : 'messages';
$validDomains = ['messages', 'admin'];
if (!in_array($domain, $validDomains)) {
    $domain = 'messages';
}
$tableName = 'translations_' . $domain;

$page = isset($_GET['page']) ? max(1, intval($_GET['page'])) : 1;
$limit = 25;
$offset = ($page - 1) * $limit;

$countResult = $conn->query("SELECT COUNT(DISTINCT `key`) as total FROM {$tableName}");
$total = $countResult->fetch_assoc()['total'];
$totalPages = ceil($total / $limit);

$searchWhere = '';
if (!empty($_GET['searchString'])) {
    $searchTerm = $conn->real_escape_string('%' . mb_strtolower($_GET['searchString']) . '%');
    $searchWhere = " WHERE LOWER(`key`) LIKE '{$searchTerm}' OR LOWER(text) LIKE '{$searchTerm}'";
}

$sql = "SELECT DISTINCT `key`, `type`, `creationDate`, `modificationDate` FROM {$tableName}{$searchWhere} GROUP BY `key` ORDER BY `key` ASC LIMIT {$limit} OFFSET {$offset}";
$result = $conn->query($sql);
$translations = [];
while ($row = $result->fetch_assoc()) {
    $translations[] = $row;
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Administration - Translations</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>CMS Admin</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="/admin/portal.php">Dashboard</a></li>
                <li><a href="/admin/documents.php">Documents</a></li>
                <li><a href="/admin/assets-manager.php">Assets</a></li>
                <li class="active"><a href="/admin/locale/data.php">Translations</a></li>
                <?php if ($_SESSION['is_admin']): ?>
                <li><a href="/admin/users.php">Users</a></li>
                <?php endif; ?>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header">
                <h1>Translations (<?php echo htmlspecialchars($domain); ?>)</h1>
                <div class="header-actions">
                    <a href="?domain=messages" class="btn <?php echo $domain === 'messages' ? 'btn-primary' : ''; ?>">Website</a>
                    <a href="?domain=admin" class="btn <?php echo $domain === 'admin' ? 'btn-primary' : ''; ?>">Admin</a>
                    <?php if ($_SESSION['is_admin']): ?>
                    <a href="/admin/locale/download.php?domain=<?php echo htmlspecialchars($domain); ?>" class="btn btn-export">Export CSV</a>
                    <?php endif; ?>
                </div>
            </div>
            <div class="filter-bar">
                <form method="GET" action="">
                    <input type="hidden" name="domain" value="<?php echo htmlspecialchars($domain); ?>">
                    <input type="text" name="searchString" placeholder="Search translations..." value="<?php echo htmlspecialchars($_GET['searchString'] ?? ''); ?>" class="search-input">
                    <button type="submit" class="btn">Search</button>
                </form>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Key</th>
                        <th>Type</th>
                        <th>Created</th>
                        <th>Modified</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($translations as $t): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($t['key']); ?></td>
                        <td><?php echo htmlspecialchars($t['type'] ?? '-'); ?></td>
                        <td><?php echo $t['creationDate'] ? date('Y-m-d H:i', $t['creationDate']) : '-'; ?></td>
                        <td><?php echo $t['modificationDate'] ? date('Y-m-d H:i', $t['modificationDate']) : '-'; ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <?php if ($totalPages > 1): ?>
            <div class="pagination">
                <?php for ($i = 1; $i <= $totalPages; $i++): ?>
                <a href="?domain=<?php echo htmlspecialchars($domain); ?>&page=<?php echo $i; ?>" class="<?php echo $i === $page ? 'active' : ''; ?>"><?php echo $i; ?></a>
                <?php endfor; ?>
            </div>
            <?php endif; ?>
            <?php if ($_SESSION['is_admin']): ?>
            <div class="export-section">
                <h3>Export</h3>
                <form id="exportForm" method="GET" action="/admin/locale/download.php">
                    <input type="hidden" name="domain" value="<?php echo htmlspecialchars($domain); ?>">
                    <div class="form-row">
                        <label>Filter by column:</label>
                        <select id="filterCol">
                            <option value="">No filter</option>
                            <option value="key">Key</option>
                            <option value="type">Type</option>
                            <option value="creationDate">Created</option>
                            <option value="modificationDate">Modified</option>
                        </select>
                        <input type="text" id="filterVal" placeholder="Filter value...">
                        <input type="hidden" name="filter" id="filterParam" value="">
                    </div>
                    <button type="submit" class="btn btn-export">Download CSV</button>
                </form>
            </div>
            <script>
            document.getElementById('exportForm').addEventListener('submit', function(e) {
                var col = document.getElementById('filterCol').value;
                var val = document.getElementById('filterVal').value;
                var filterInput = document.getElementById('filterParam');
                if (col && val) {
                    filterInput.value = JSON.stringify([{"property": col, "value": val, "type": "string"}]);
                } else {
                    filterInput.value = '';
                }
            });
            </script>
            <?php endif; ?>
        </main>
    </div>
</body>
</html>
