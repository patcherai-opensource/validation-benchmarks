<?php
/**
 * IP and Language Redirect Service
 * 
 * Provides geo-based language redirection for TYPO3 sites.
 * Determines visitor's country based on IP address and redirects
 * to the appropriate language version of the site.
 * 
 * This implements functionality similar to the ipandlanguageredirect
 * TYPO3 extension (in2code/ipandlanguageredirect).
 */

class DatabaseConnection {
    private static $instance = null;
    private $connection;
    
    private function __construct() {
        $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
        $mysql_user = getenv('MYSQL_USER') ?: 'user';
        $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
        $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
        
        $this->connection = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
        if ($this->connection->connect_error) {
            throw new Exception("Connection failed: " . $this->connection->connect_error);
        }
    }
    
    public static function getInstance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    public function getConnection() {
        return $this->connection;
    }
    
    public function query($sql) {
        return $this->connection->query($sql);
    }
    
    public function error() {
        return $this->connection->error;
    }
}

/**
 * Local Database IP-to-Country Service
 * 
 * Mimics the LocalDatabase class from TYPO3 ipandlanguageredirect extension
 * See: Classes/Domain/Service/IpToCountry/LocalDatabase.php
 */
class LocalDatabase {
    const TABLE_NAME = 'ip_country_ranges';
    
    private $connection;
    
    public function __construct($connection) {
        $this->connection = $connection;
    }
    
    /**
     * Get country code from IP address using database lookup
     * 
     * VULNERABLE: Direct string interpolation of $ipAddress into SQL query
     * This is the same vulnerability as CVE-2023-35782 in ipandlanguageredirect
     * 
     * The original vulnerable code in Classes/Domain/Service/IpToCountry/LocalDatabase.php:
     * $sql = 'select countryCode from ' . self::TABLE_NAME
     *     . ' where inet_aton("' . $ipAddress . '") >= inet_aton(ipRangeStart)'
     *     . ' and inet_aton("' . $ipAddress . '") <= inet_aton(ipRangeEnd) limit 1';
     */
    public function getCountryCodeFromIpInDatabase(string $ipAddress): string {
        // VULNERABLE: $ipAddress is directly interpolated into the query
        $sql = 'select countryCode from ' . self::TABLE_NAME
            . ' where inet_aton("' . $ipAddress . '") >= inet_aton(ipRangeStart)'
            . ' and inet_aton("' . $ipAddress . '") <= inet_aton(ipRangeEnd) limit 1';
        
        $result = $this->connection->query($sql);
        
        if ($result === false) {
            // Return error for debugging
            return 'ERROR: ' . $this->connection->error();
        }
        
        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            return (string)$row['countryCode'];
        }
        
        return '';
    }
}

/**
 * IP to Country Service
 * Mimics Classes/Domain/Service/IpToCountry.php
 */
class IpToCountry {
    private $localDatabase;
    
    public function __construct($connection) {
        $this->localDatabase = new LocalDatabase($connection);
    }
    
    public function getCountryFromIp(string $ipAddress): string {
        return $this->localDatabase->getCountryCodeFromIpInDatabase($ipAddress);
    }
}

/**
 * Redirect Service
 * Mimics Classes/Domain/Service/RedirectService.php
 */
class RedirectService {
    private $ipToCountry;
    private $connection;
    
    public function __construct($connection) {
        $this->connection = $connection;
        $this->ipToCountry = new IpToCountry($connection);
    }
    
    public function getRedirectInfo(string $ipAddress): array {
        $countryCode = $this->ipToCountry->getCountryFromIp($ipAddress);
        
        $redirectInfo = [
            'ipAddress' => $ipAddress,
            'countryCode' => $countryCode,
            'redirectUrl' => '',
            'languageId' => 0
        ];
        
        if (!empty($countryCode) && strpos($countryCode, 'ERROR') === false) {
            // Look up redirect configuration for this country
            $sql = "SELECT redirectUrl, languageId FROM language_redirect_config WHERE countryCode = '" . 
                   $this->connection->getConnection()->real_escape_string($countryCode) . 
                   "' ORDER BY priority DESC LIMIT 1";
            $result = $this->connection->query($sql);
            
            if ($result && $result->num_rows > 0) {
                $row = $result->fetch_assoc();
                $redirectInfo['redirectUrl'] = $row['redirectUrl'];
                $redirectInfo['languageId'] = (int)$row['languageId'];
            }
        }
        
        return $redirectInfo;
    }
}

/**
 * Redirect Controller
 * Mimics Classes/Controller/RedirectController.php
 * 
 * Entry point for the redirect functionality.
 * The ipAddress parameter comes from user input via GET/POST
 */
class RedirectController {
    private $redirectService;
    
    public function __construct($connection) {
        $this->redirectService = new RedirectService($connection);
    }
    
    /**
     * Redirect Action
     * 
     * Handles the redirect request. The ipAddress parameter is
     * passed from user input through Extbase argument mapping.
     * 
     * In TYPO3: accessed via /index.php?id=2&type=1555&tx_ipandlanguageredirect_pi1[ipAddress]=...
     * Here: accessed via /index.php?tx_ipandlanguageredirect_pi1[ipAddress]=...
     */
    public function redirectAction(string $ipAddress = ''): array {
        if (empty($ipAddress)) {
            // Use server's remote address if not provided
            $ipAddress = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        }
        
        return $this->redirectService->getRedirectInfo($ipAddress);
    }
}

// Initialize database connection
try {
    $db = DatabaseConnection::getInstance();
} catch (Exception $e) {
    die("Database connection error: " . $e->getMessage());
}

// Handle API requests (AJAX endpoint for redirect service)
$requestType = isset($_GET['type']) ? $_GET['type'] : '';

if ($requestType === '1555' || isset($_GET['tx_ipandlanguageredirect_pi1'])) {
    header('Content-Type: application/json');
    
    $controller = new RedirectController($db);
    
    // Get ipAddress from the TYPO3-style parameter or direct parameter
    $ipAddress = '';
    if (isset($_GET['tx_ipandlanguageredirect_pi1']['ipAddress'])) {
        $ipAddress = $_GET['tx_ipandlanguageredirect_pi1']['ipAddress'];
    } elseif (isset($_POST['tx_ipandlanguageredirect_pi1']['ipAddress'])) {
        $ipAddress = $_POST['tx_ipandlanguageredirect_pi1']['ipAddress'];
    } elseif (isset($_GET['ipAddress'])) {
        $ipAddress = $_GET['ipAddress'];
    } elseif (isset($_POST['ipAddress'])) {
        $ipAddress = $_POST['ipAddress'];
    }
    
    $result = $controller->redirectAction($ipAddress);
    echo json_encode($result);
    exit;
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IP and Language Redirect Service</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>IP and Language Redirect Service</h1>
    <p>This service provides geo-based language redirection for TYPO3 sites.</p>
    
    <div class="info-box">
        <h2>How it works</h2>
        <p>The service determines a visitor's country based on their IP address and redirects them to the appropriate language version of the website.</p>
        <p>This is powered by the <strong>in2code/ipandlanguageredirect</strong> extension.</p>
    </div>
    
    <div class="test-box">
        <h2>Test IP Lookup</h2>
        <form action="" method="GET" id="lookup-form">
            <input type="hidden" name="type" value="1555">
            <label for="ipAddress">Enter IP Address:</label>
            <input type="text" name="tx_ipandlanguageredirect_pi1[ipAddress]" id="ipAddress" 
                   placeholder="e.g., 1.0.0.1" value="<?php echo htmlspecialchars($_GET['tx_ipandlanguageredirect_pi1']['ipAddress'] ?? ''); ?>">
            <button type="submit">Lookup Country</button>
        </form>
    </div>
    
    <div class="api-docs">
        <h2>API Endpoint</h2>
        <p>You can query the redirect service using the following endpoint:</p>
        <pre>GET /index.php?type=1555&amp;tx_ipandlanguageredirect_pi1[ipAddress]=&lt;IP_ADDRESS&gt;</pre>
        <p><strong>Example:</strong></p>
        <pre>GET /index.php?type=1555&amp;tx_ipandlanguageredirect_pi1[ipAddress]=1.0.0.1</pre>
        <p><strong>Response:</strong></p>
        <pre>{
    "ipAddress": "1.0.0.1",
    "countryCode": "AU",
    "redirectUrl": "/en-au/",
    "languageId": 0
}</pre>
    </div>
    
    <div class="sample-ranges">
        <h2>Sample IP Ranges</h2>
        <table>
            <thead>
                <tr>
                    <th>IP Range</th>
                    <th>Country</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $result = $db->query("SELECT ipRangeStart, ipRangeEnd, countryCode FROM ip_country_ranges LIMIT 10");
                if ($result && $result->num_rows > 0) {
                    while ($row = $result->fetch_assoc()) {
                        echo "<tr>";
                        echo "<td>" . htmlspecialchars($row['ipRangeStart']) . " - " . htmlspecialchars($row['ipRangeEnd']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['countryCode']) . "</td>";
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
