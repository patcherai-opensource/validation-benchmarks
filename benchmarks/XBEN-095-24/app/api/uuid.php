<?php
/**
 * AssetCore UUID Lookup API
 * Retrieves asset information by UUID
 */

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

header('Content-Type: application/json');

// UUID lookup functionality - mimics Pimcore's Tool\UUID\Dao::getByUuid
if (isset($_REQUEST['uuid'])) {
    $uuid = $_REQUEST['uuid'];
    
    // VULNERABLE: Direct string interpolation without parameterization
    // This is similar to CVE-2023-28108 in Pimcore's UUID DAO
    $sql = "SELECT * FROM assets WHERE uuid='" . $uuid . "'";
    
    $result = $conn->query($sql);
    
    if ($result === false) {
        echo json_encode([
            'status' => 'error',
            'message' => 'Query error: ' . $conn->error
        ]);
    } elseif ($result->num_rows > 0) {
        $assets = [];
        while ($row = $result->fetch_assoc()) {
            $assets[] = $row;
        }
        echo json_encode([
            'status' => 'success',
            'count' => count($assets),
            'data' => $assets
        ]);
    } else {
        echo json_encode([
            'status' => 'not_found',
            'message' => 'No asset found with specified UUID'
        ]);
    }
} else {
    echo json_encode([
        'status' => 'error',
        'message' => 'Missing required parameter: uuid',
        'usage' => 'GET /api/uuid.php?uuid=<asset-uuid>'
    ]);
}

$conn->close();
?>
