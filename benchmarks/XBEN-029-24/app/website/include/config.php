<?php

require_once(__DIR__ . '/db_config.php');

function getAllowedFileTypes() {
    global $db_connect;
    $result = mysqli_query($db_connect, "SELECT config_value FROM site_config WHERE config_key = 'allowed_file_types'");
    if ($result && $row = mysqli_fetch_assoc($result)) {
        return array_map('trim', explode(',', $row['config_value']));
    }
    return array('jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'pdf');
}

function getConfig($key) {
    global $db_connect;
    $stmt = mysqli_prepare($db_connect, "SELECT config_value FROM site_config WHERE config_key = ?");
    mysqli_stmt_bind_param($stmt, "s", $key);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    if ($row = mysqli_fetch_assoc($result)) {
        return $row['config_value'];
    }
    return null;
}

?>
