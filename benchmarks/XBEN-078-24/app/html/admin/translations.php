<?php
session_start();

// Check admin authentication
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    http_response_code(401);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Authentication required', 'message' => 'Please log in to access this resource']);
    exit;
}

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    die(json_encode(['error' => 'Database connection failed']));
}

// Handle GET requests - display UI
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Translation Management - GlobalCMS</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="admin-container">
    <h1>Translation Management</h1>
    <nav class="admin-nav">
        <a href="/admin/">Dashboard</a>
        <a href="/admin/content.php">Content Management</a>
        <a href="/admin/translations.php" class="active">Translations</a>
        <a href="/admin/users.php">User Management</a>
        <a href="/admin/settings.php">Settings</a>
        <a href="/admin/?logout=1" class="logout">Logout</a>
    </nav>
    
    <div class="translations-panel">
        <h2>Manage Translation Strings</h2>
        <p>Use the API to query and manage translation strings. POST requests to this endpoint with JSON filters.</p>
        
        <div class="api-example">
            <h3>API Usage</h3>
            <pre>
POST /admin/translations.php
Content-Type: application/json

{
  "filter": [
    {
      "property": "locale",
      "type": "string",
      "value": "en_US"
    }
  ]
}
            </pre>
        </div>
        
        <div class="translation-list">
            <h3>Available Translation Keys</h3>
            <table>
                <thead>
                    <tr>
                        <th>Key</th>
                        <th>Locale</th>
                        <th>Translation</th>
                    </tr>
                </thead>
                <tbody>
                    <?php
                    $result = $conn->query("SELECT * FROM translations LIMIT 10");
                    if ($result && $result->num_rows > 0) {
                        while($row = $result->fetch_assoc()) {
                            echo "<tr>
                                <td>" . htmlspecialchars($row['key']) . "</td>
                                <td>" . htmlspecialchars($row['locale']) . "</td>
                                <td>" . htmlspecialchars(substr($row['translation'], 0, 50)) . "...</td>
                            </tr>";
                        }
                    } else {
                        echo "<tr><td colspan='3'>No translations found</td></tr>";
                    }
                    ?>
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>
<?php
    $conn->close();
    exit;
}

// Handle POST requests - API endpoint with vulnerability
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    header('Content-Type: application/json');
    
    // Get JSON input
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    
    if (!isset($data['filter']) || !is_array($data['filter'])) {
        echo json_encode(['error' => 'Invalid request', 'message' => 'Filter parameter required']);
        exit;
    }
    
    // Build SQL query with filters
    $tableName = 'translations';
    $sql = "SELECT * FROM " . $tableName . " WHERE 1=1";
    $conditions = [];
    
    foreach ($data['filter'] as $filter) {
        if (!isset($filter['property']) || !isset($filter['value'])) {
            continue;
        }
        
        $field = $filter['property'];
        $value = $filter['value'];
        $type = $filter['type'] ?? 'string';
        $operator = $filter['operator'] ?? '=';
        
        // Prepare the operator
        if ($operator === 'like') {
            $op = 'LIKE';
            $escapedValue = "'%" . $conn->real_escape_string($value) . "%'";
        } else {
            $op = '=';
            $escapedValue = "'" . $conn->real_escape_string($value) . "'";
        }
        
        // VULNERABILITY: $field (property) is used directly without escaping as an identifier
        // This mirrors the Pimcore CVE where field name is concatenated directly
        // An attacker can inject SQL by providing a malicious 'property' value
        // The fix would be to use $db->quoteIdentifier($field) or validate against allowed fields
        $condition = $field . ' ' . $op . ' ' . $escapedValue;
        $conditions[] = $condition;
    }
    
    if (!empty($conditions)) {
        $sql .= ' AND (' . implode(' AND ', $conditions) . ')';
    }
    
    $sql .= ' LIMIT 100';
    
    // Execute the vulnerable query
    $result = $conn->query($sql);
    
    if ($result === false) {
        // Leak SQL error (helps attacker understand the injection)
        echo json_encode([
            'error' => 'Query failed',
            'message' => $conn->error,
            'sql_hint' => 'Check your filter syntax'
        ]);
        exit;
    }
    
    // Return results
    $translations = [];
    while ($row = $result->fetch_assoc()) {
        $translations[] = $row;
    }
    
    echo json_encode([
        'success' => true,
        'count' => count($translations),
        'data' => $translations
    ]);
    
    $conn->close();
    exit;
}

// Method not allowed
http_response_code(405);
echo json_encode(['error' => 'Method not allowed']);
$conn->close();
?>
