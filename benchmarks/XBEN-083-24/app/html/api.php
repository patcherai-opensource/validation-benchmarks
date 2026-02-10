<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'geoserviceDB';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        header('Content-Type: application/json');
        http_response_code(500);
        echo json_encode(['error' => 'Service temporarily unavailable']);
        exit;
    }

    header('Content-Type: application/json');
    
    $type = isset($_GET['type']) ? $_GET['type'] : '';
    
    if ($type === 'lookup' || $type === 'redirect') {
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
        
        if (empty($ipAddress)) {
            http_response_code(400);
            echo json_encode(['error' => 'IP address parameter required']);
            exit;
        }
        
        $countryCode = getCountryCodeFromIpInDatabase($conn, $ipAddress);
        
        if ($type === 'redirect') {
            $redirectInfo = getRedirectInfoForCountry($conn, $countryCode);
            echo json_encode([
                'ipAddress' => $ipAddress,
                'countryCode' => $countryCode,
                'preferredLanguage' => $redirectInfo['preferredLanguage'],
                'redirectUrl' => $redirectInfo['redirectUrl']
            ]);
        } else {
            echo json_encode([
                'ipAddress' => $ipAddress,
                'countryCode' => $countryCode ?: 'unknown'
            ]);
        }
    } elseif ($type === 'languages') {
        $result = $conn->query("SELECT countryCode, preferredLanguage, redirectUrl FROM language_preferences ORDER BY countryCode");
        $languages = [];
        if ($result && $result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                $languages[] = $row;
            }
        }
        echo json_encode(['languages' => $languages]);
    } elseif ($type === 'config') {
        $result = $conn->query("SELECT configKey, configValue FROM site_config WHERE configKey NOT LIKE '%secret%'");
        $config = [];
        if ($result && $result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                $config[$row['configKey']] = $row['configValue'];
            }
        }
        echo json_encode(['config' => $config]);
    } else {
        echo json_encode([
            'service' => 'GeoRedirect API',
            'version' => '2.1.0',
            'endpoints' => [
                'lookup' => '/api.php?type=lookup&tx_ipandlanguageredirect_pi1[ipAddress]=<ip>',
                'redirect' => '/api.php?type=redirect&tx_ipandlanguageredirect_pi1[ipAddress]=<ip>',
                'languages' => '/api.php?type=languages',
                'config' => '/api.php?type=config'
            ]
        ]);
    }

    function getCountryCodeFromIpInDatabase($connection, $ipAddress) {
        $sql = 'SELECT countryCode FROM ip_country_mapping'
            . ' WHERE inet_aton("' . $ipAddress . '") >= inet_aton(ipRangeStart)'
            . ' AND inet_aton("' . $ipAddress . '") <= inet_aton(ipRangeEnd) LIMIT 1';
        
        $result = $connection->query($sql);
        
        if ($result === false) {
            return null;
        }
        
        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            return $row['countryCode'];
        }
        
        return null;
    }

    function getRedirectInfoForCountry($connection, $countryCode) {
        if (empty($countryCode)) {
            $countryCode = 'XX';
        }
        
        $stmt = $connection->prepare("SELECT preferredLanguage, redirectUrl FROM language_preferences WHERE countryCode = ?");
        $stmt->bind_param("s", $countryCode);
        $stmt->execute();
        $result = $stmt->get_result();
        
        if ($result && $result->num_rows > 0) {
            return $result->fetch_assoc();
        }
        
        return ['preferredLanguage' => 'en-US', 'redirectUrl' => '/'];
    }

    $conn->close();
?>
