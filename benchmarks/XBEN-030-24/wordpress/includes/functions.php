<?php

function ensureCSRFSessionToken()
{
    if (!isset($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
}

function CSRFTokenFieldTag()
{
    return '<input type="hidden" name="csrf_token" value="'.$_SESSION['csrf_token'].'">';
}

function CSRFMetaTag()
{
    return '<meta name="csrf_token" content="'.$_SESSION['csrf_token'].'">';
}

function CSRFValidate()
{
    $token = $_POST['csrf_token'] ?? $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';
    if (empty($token) || empty($_SESSION['csrf_token'])) {
        return false;
    }
    return hash_equals($_SESSION['csrf_token'], $token);
}

function csrfValidateRequest()
{
    return $_SERVER['REQUEST_METHOD'] === 'POST';
}

function handleInvalidCSRFToken()
{
    header('HTTP/1.1 403 Forbidden');
    echo json_encode(['error' => 'CSRF token validation failed']);
    exit;
}

function renderTemplate($name, $data = [])
{
    extract($data);
    ob_start();
    include(__DIR__ . '/../templates/' . $name . '.php');
    return ob_get_clean();
}

function getHumanReadableDatasize($numbytes, $precision = 2)
{
    $humanDatasize = '';
    $kib = 1024;
    $mib = $kib * 1024;
    $gib = $mib * 1024;
    if ($numbytes >= $gib) {
        $humanDatasize = round($numbytes / $gib, $precision).' GB';
    } elseif ($numbytes >= $mib) {
        $humanDatasize = round($numbytes / $mib, $precision).' MB';
    } elseif ($numbytes >= $kib) {
        $humanDatasize = round($numbytes / $kib, $precision).' KB';
    } else {
        $humanDatasize = $numbytes.' B';
    }
    return $humanDatasize;
}
