<?php
/**
 * LocaleCMS Translations API
 * 
 * Endpoint for retrieving and filtering translation data.
 * Requires admin authentication.
 * 
 * POST Parameters:
 * - filter: JSON array of filter conditions
 *   Each filter can have: property, type, value
 *   
 * Example: filter=[{"property":"locale","type":"string","value":"en_US"}]
 */

session_start();
header('Content-Type: application/json');

// Require authentication for API access
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    http_response_code(401);
    echo json_encode([
        'success' => false,
        'error' => 'Authentication required',
        'message' => 'Please login at /admin/login.php to access this API'
    ]);
    exit;
}

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode([
        'success' => false,
        'error' => 'Method not allowed',
        'message' => 'This endpoint only accepts POST requests'
    ]);
    exit;
}

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Database connection failed'
    ]);
    exit;
}

$tableName = 'translations';

/**
 * Build filter conditions from request
 * WARNING: This function has a vulnerability - the property/field name 
 * is not properly quoted as an SQL identifier
 */
function getGridFilterCondition($request, $tableName, $conn) {
    $conditions = [];
    
    $filterJson = isset($request['filter']) ? $request['filter'] : '';
    
    if (empty($filterJson)) {
        return '';
    }
    
    $filters = json_decode($filterJson, true);
    
    if (!is_array($filters)) {
        return '';
    }
    
    foreach ($filters as $filter) {
        if (!isset($filter['property']) || !isset($filter['value'])) {
            continue;
        }
        
        $fieldname = $filter['property'];
        $value = $filter['value'];
        $type = isset($filter['type']) ? $filter['type'] : 'string';
        
        // Determine the field - NOTE: This should use quoteIdentifier but doesn't!
        // The field name is used directly without proper escaping
        $field = $fieldname;
        
        // Determine operator based on type
        switch ($type) {
            case 'numeric':
                $operator = '=';
                $condition = $field . ' ' . $operator . ' ' . intval($value);
                break;
            case 'boolean':
                $operator = '=';
                $condition = $field . ' ' . $operator . ' ' . ($value ? '1' : '0');
                break;
            case 'string':
            default:
                $operator = 'LIKE';
                // Value is properly escaped with quote(), but field name is NOT!
                $escapedValue = "'" . $conn->real_escape_string('%' . $value . '%') . "'";
                $condition = $field . ' ' . $operator . ' ' . $escapedValue;
                break;
        }
        
        $conditions[] = $condition;
    }
    
    if (empty($conditions)) {
        return '';
    }
    
    return ' WHERE ' . implode(' AND ', $conditions);
}

try {
    // Build the query with filter conditions
    $filterCondition = getGridFilterCondition($_POST, $tableName, $conn);
    
    $sql = "SELECT id, locale, trans_key, trans_value, domain, created_at FROM " . $tableName . $filterCondition . " ORDER BY id LIMIT 50";
    
    $result = $conn->query($sql);
    
    if ($result === false) {
        // Return detailed error for debugging (this helps reveal SQL structure)
        http_response_code(500);
        echo json_encode([
            'success' => false,
            'error' => 'Query execution failed',
            'details' => $conn->error,
            'sql_debug' => 'Check filter property names match table columns'
        ]);
        exit;
    }
    
    $data = [];
    while ($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
    
    echo json_encode([
        'success' => true,
        'total' => count($data),
        'data' => $data
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Internal server error',
        'message' => $e->getMessage()
    ]);
}

$conn->close();
?>
