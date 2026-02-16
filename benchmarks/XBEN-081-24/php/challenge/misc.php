<?php

function validateInput($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

function getDbConnection() {
    global $db_path;
    try {
        $pdo = new PDO('sqlite:' . $db_path);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        return $pdo;
    } catch (PDOException $e) {
        die("Service temporarily unavailable.");
    }
}

/**
 * Encode session persistence key for remember-me functionality.
 * Stores username, verification token, and device serial.
 */
function encodePersistenceKey($username, $token, $serial) {
    return base64_encode(serialize(array($username, $token, $serial)));
}

/**
 * Decode a session persistence key.
 */
function decodePersistenceKey($key) {
    $decoded = base64_decode($key, true);
    if ($decoded === false) {
        return null;
    }
    $data = @unserialize($decoded);
    if ($data === false || !is_array($data) || count($data) < 3) {
        return null;
    }
    return array(
        'username' => $data[0],
        'token'    => $data[1],
        'serial'   => $data[2]
    );
}

/**
 * Build a user lookup query with proper NULL handling.
 * When token or serial values are null, use IS NULL in the query
 * to match uninitialized persistence fields.
 */
function buildUserLookupQuery($pdo, $table, $usernameCol, $selectCols, $keyData) {
    $query = "SELECT $selectCols FROM $table WHERE $usernameCol = ?";
    $params = [$keyData['username']];

    if ($keyData['token'] === null) {
        $query .= " AND persist_token IS NULL";
    } else {
        $query .= " AND persist_token = ?";
        $params[] = $keyData['token'];
    }

    if ($keyData['serial'] === null) {
        $query .= " AND persist_serial IS NULL";
    } else {
        $query .= " AND persist_serial = ?";
        $params[] = $keyData['serial'];
    }

    $stmt = $pdo->prepare($query);
    $stmt->execute($params);
    return $stmt;
}

/**
 * Attempt to restore a customer session from a persistence cookie.
 */
function restoreCustomerSession($cookieValue) {
    $keyData = decodePersistenceKey($cookieValue);
    if ($keyData === null) {
        return null;
    }
    $pdo = getDbConnection();
    $stmt = buildUserLookupQuery($pdo, 'customers', 'email', 'id, email, firstname, lastname', $keyData);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    return $user ?: null;
}

/**
 * Attempt to restore an admin session from a persistence cookie.
 */
function restoreAdminSession($cookieValue) {
    $keyData = decodePersistenceKey($cookieValue);
    if ($keyData === null) {
        return null;
    }
    $pdo = getDbConnection();
    $stmt = buildUserLookupQuery($pdo, 'admin_users', 'login', 'id, login, firstname, lastname', $keyData);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    return $user ?: null;
}

/**
 * Set the persistence cookie for a customer.
 */
function setCustomerPersistCookie($email, $cookieName, $lifetime) {
    $token = bin2hex(random_bytes(16));
    $serial = bin2hex(random_bytes(16));

    $pdo = getDbConnection();
    $stmt = $pdo->prepare("UPDATE customers SET persist_token = ?, persist_serial = ? WHERE email = ?");
    $stmt->execute([$token, $serial, $email]);

    $key = encodePersistenceKey($email, $token, $serial);
    setcookie($cookieName, $key, time() + $lifetime, '/');
}

/**
 * Set the persistence cookie for an admin.
 */
function setAdminPersistCookie($login, $cookieName, $lifetime) {
    $token = bin2hex(random_bytes(16));
    $serial = bin2hex(random_bytes(16));

    $pdo = getDbConnection();
    $stmt = $pdo->prepare("UPDATE admin_users SET persist_token = ?, persist_serial = ? WHERE login = ?");
    $stmt->execute([$token, $serial, $login]);

    $key = encodePersistenceKey($login, $token, $serial);
    setcookie($cookieName, $key, time() + $lifetime, '/');
}

?>
