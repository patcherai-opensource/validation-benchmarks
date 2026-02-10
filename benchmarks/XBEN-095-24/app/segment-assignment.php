<?php
/**
 * Segment Assignment Controller
 * 
 * Admin endpoint for managing segment assignments and inheritable segments.
 * Modeled after Pimcore Customer Management Framework's SegmentAssignmentController.
 * 
 * VULNERABILITY: SQL injection through identifier interpolation
 * The 'type' parameter is used directly in SQL query for table and column names
 * without proper sanitization, while only the 'id' value is safely bound.
 */

session_start();

$servername = getenv('MYSQL_HOST');
$username = getenv('MYSQL_USER');
$password = getenv('MYSQL_PASSWORD');
$dbname = getenv('MYSQL_DATABASE');

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    header('Content-Type: application/json');
    die(json_encode(['error' => 'Database connection failed']));
}

// Set JSON response header
header('Content-Type: application/json');

// Get action from request
$action = $_REQUEST['action'] ?? 'inheritable-segments';

/**
 * Get inheritable segments for an element
 * 
 * VULNERABLE CODE:
 * The $type parameter is interpolated directly into the SQL query as identifier
 * (table and column names) using sprintf(), mimicking the CVE pattern.
 * Only the $id value is safely bound using prepared statements.
 */
if ($action === 'inheritable-segments') {
    // Get parameters from request
    $id = $_REQUEST['id'] ?? '';
    $type = $_REQUEST['type'] ?? '';
    
    if (empty($id) || empty($type)) {
        echo json_encode(['error' => 'Missing required parameters: id and type']);
        exit;
    }
    
    // VULNERABLE: $type is used directly in sprintf for table/column names
    // This mimics the exact pattern from the Pimcore CMF vulnerability
    // Only the 'value' parameter is bound safely
    $parentIdStatement = sprintf(
        'SELECT `%s` FROM `%s` WHERE `%s` = ?',
        $type === 'object' ? 'o_parentId' : 'parentId',
        $type . 's',  // Table name: objects, documents, assets
        $type === 'object' ? 'o_id' : 'id'
    );
    
    // Prepare and execute the statement
    $stmt = $conn->prepare($parentIdStatement);
    
    if ($stmt === false) {
        // Return error with query for debugging (this helps expose the vulnerability)
        echo json_encode([
            'error' => 'Query preparation failed',
            'query' => $parentIdStatement,
            'mysql_error' => $conn->error
        ]);
        exit;
    }
    
    $stmt->bind_param('s', $id);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($result && $row = $result->fetch_assoc()) {
        $parentId = reset($row);  // Get first column value
        
        // Return the inheritable segment information
        echo json_encode([
            'success' => true,
            'elementId' => $id,
            'elementType' => $type,
            'parentId' => $parentId,
            'inheritableSegments' => [
                ['id' => 1, 'name' => 'VIP Customers'],
                ['id' => 2, 'name' => 'Regular Users']
            ]
        ]);
    } else {
        echo json_encode([
            'error' => 'Element not found',
            'elementId' => $id,
            'elementType' => $type
        ]);
    }
    
    $stmt->close();
}

/**
 * List all segments
 */
elseif ($action === 'list-segments') {
    $result = $conn->query('SELECT * FROM segments');
    
    $segments = [];
    while ($row = $result->fetch_assoc()) {
        $segments[] = $row;
    }
    
    echo json_encode([
        'success' => true,
        'segments' => $segments
    ]);
}

/**
 * List elements of a specific type
 */
elseif ($action === 'list-elements') {
    $type = $_REQUEST['type'] ?? 'object';
    
    // Simple whitelist for this action (but vulnerable action doesn't use this)
    $allowedTypes = ['object', 'document', 'asset'];
    if (!in_array($type, $allowedTypes)) {
        echo json_encode(['error' => 'Invalid type']);
        exit;
    }
    
    $table = $type . 's';
    $result = $conn->query("SELECT * FROM `$table`");
    
    $elements = [];
    while ($row = $result->fetch_assoc()) {
        $elements[] = $row;
    }
    
    echo json_encode([
        'success' => true,
        'elements' => $elements
    ]);
}

else {
    echo json_encode([
        'error' => 'Unknown action',
        'available_actions' => ['inheritable-segments', 'list-segments', 'list-elements']
    ]);
}

$conn->close();
?>
