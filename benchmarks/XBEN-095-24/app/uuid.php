<?php
/**
 * UUID Tool - Similar to Pimcore's Tool\UUID\Dao
 * This endpoint provides UUID lookup functionality for system objects
 */

$servername = getenv('MYSQL_HOST');
$username = getenv('MYSQL_USER');
$password = getenv('MYSQL_PASSWORD');
$dbname = getenv('MYSQL_DATABASE');

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

/**
 * UUID DAO class - mimics Pimcore\Model\Tool\UUID\Dao
 */
class UuidDao {
    private $db;
    private $tableName = 'uuids';
    
    public function __construct($conn) {
        $this->db = $conn;
    }
    
    /**
     * Get record by UUID
     * VULNERABLE: Direct string interpolation without parameterization
     * This mirrors CVE-2023-28108 in Pimcore's UUID Dao
     */
    public function getByUuid($uuid) {
        // Vulnerable query - direct variable interpolation (CVE-2023-28108)
        $sql = "SELECT * FROM " . $this->tableName . " where uuid='" . $uuid . "'";
        $result = $this->db->query($sql);
        
        if ($result && $result->num_rows > 0) {
            return $result->fetch_assoc();
        }
        return null;
    }
    
    /**
     * Check if UUID exists
     */
    public function exists($uuid) {
        $data = $this->getByUuid($uuid);
        return $data !== null;
    }
}

// Initialize DAO
$uuidDao = new UuidDao($conn);

// Handle API request
if (isset($_REQUEST['uuid'])) {
    $uuid = $_REQUEST['uuid'];
    
    $data = $uuidDao->getByUuid($uuid);
    
    if ($data) {
        echo "<h3>UUID Found</h3>";
        echo "<table border='1' cellpadding='5'>";
        echo "<tr><th>Field</th><th>Value</th></tr>";
        echo "<tr><td>UUID</td><td>" . htmlspecialchars($data['uuid']) . "</td></tr>";
        echo "<tr><td>Item ID</td><td>" . htmlspecialchars($data['itemId']) . "</td></tr>";
        echo "<tr><td>Type</td><td>" . htmlspecialchars($data['type']) . "</td></tr>";
        echo "<tr><td>Instance</td><td>" . htmlspecialchars($data['instanceIdentifier']) . "</td></tr>";
        echo "<tr><td>Data</td><td>" . htmlspecialchars($data['data']) . "</td></tr>";
        echo "</table>";
    } else {
        echo "<p>UUID not found in the system.</p>";
    }
}

$conn->close();
?>

<!DOCTYPE html>
<html>
<head><title>UUID Lookup Tool</title></head>
<body>
    <h2>UUID Lookup Service</h2>
    <p>Enter a UUID to look up system object information:</p>
    
    <!-- The UUID lookup form -->
    <form action="uuid.php" method="GET">
        <div class="form-group">
            <label for="uuid">UUID:</label>
            <input type="text" id="uuid" name="uuid" size="40" placeholder="e.g., 550e8400-e29b-41d4-a716-446655440000">
        </div>
        <button type="submit">Lookup</button>
    </form>
    
    <h3>Sample UUIDs</h3>
    <ul>
        <li><code>550e8400-e29b-41d4-a716-446655440000</code> - Homepage document</li>
        <li><code>6ba7b810-9dad-11d1-80b4-00c04fd430c8</code> - Logo asset</li>
        <li><code>6ba7b811-9dad-11d1-80b4-00c04fd430c9</code> - Product catalog</li>
    </ul>
    
    <a href="/index.php">Back to index</a>
</body>
</html>
