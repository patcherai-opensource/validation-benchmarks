<?php
/**
 * Translation Controller - Admin API
 * 
 * Endpoint: POST /admin/translation/translations
 * 
 * This endpoint handles translation queries with optional filters.
 * Similar to Pimcore's TranslationController::translationsAction
 */

session_start();
header('Content-Type: application/json');

// Require admin authentication
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    http_response_code(401);
    echo json_encode(['error' => 'Authentication required. Please login first.']);
    exit;
}

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed. Use POST.']);
    exit;
}

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['error' => 'Database connection failed']);
    exit;
}

$tableName = 'translations';

/**
 * Get grid filter condition from request
 * VULNERABLE: The property field is directly used as an SQL identifier without proper quoting
 * 
 * This mimics the vulnerable pattern in Pimcore's getGridFilterCondition function
 * where $field (from user input 'property') is concatenated directly into SQL
 */
function getGridFilterCondition($filters, $conn, $tableName) {
    $conditions = [];
    
    foreach ($filters as $filter) {
        if (!isset($filter['property']) || !isset($filter['value'])) {
            continue;
        }
        
        $fieldname = $filter['property'];
        $type = isset($filter['type']) ? $filter['type'] : 'string';
        $value = $filter['value'];
        
        // Process the field name (this is where the vulnerability is)
        // In the real CVE, this would go through some transformations but still end up unquoted
        $field = $fieldname;
        
        // Determine operator based on type
        switch ($type) {
            case 'numeric':
                $operator = '=';
                $quotedValue = intval($value);
                break;
            case 'boolean':
                $operator = '=';
                $quotedValue = $value ? '1' : '0';
                break;
            case 'string':
            default:
                $operator = 'LIKE';
                $quotedValue = "'" . $conn->real_escape_string('%' . $value . '%') . "'";
                break;
        }
        
        // VULNERABLE LINE: $field is NOT quoted as an SQL identifier
        // This is exactly the pattern from the CVE where user-controlled input
        // becomes part of the SQL identifier (left side of condition)
        $condition = $field . ' ' . $operator . ' ' . $quotedValue;
        $conditions[] = $condition;
    }
    
    return implode(' AND ', $conditions);
}

// Parse input
$input = file_get_contents('php://input');
$data = json_decode($input, true);

// Build base query
$sql = "SELECT * FROM " . $tableName;

// Process filters if provided
if (isset($data['filter']) && is_array($data['filter'])) {
    $filterCondition = getGridFilterCondition($data['filter'], $conn, $tableName);
    if (!empty($filterCondition)) {
        $sql .= " WHERE " . $filterCondition;
    }
}

$sql .= " LIMIT 100";

// Execute query
$result = $conn->query($sql);

if ($result === false) {
    // Return SQL error for debugging (in production, this would be logged)
    http_response_code(500);
    echo json_encode([
        'error' => 'Query error',
        'message' => $conn->error,
        'query' => $sql
    ]);
    $conn->close();
    exit;
}

// Build response
$translations = [];
while ($row = $result->fetch_assoc()) {
    $translations[] = $row;
}

echo json_encode([
    'success' => true,
    'total' => count($translations),
    'data' => $translations
]);

$conn->close();
