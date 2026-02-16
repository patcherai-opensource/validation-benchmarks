<?php

$db_host = "localhost";
$db_user = "sc_admin";
$db_pass = 'Cr@ftSecure2024';
$db_name = "sitecraft";

$db_connect = mysqli_connect($db_host, $db_user, $db_pass, $db_name);

if (!$db_connect) {
    http_response_code(500);
    die(json_encode(array("error" => "Service temporarily unavailable")));
}

?>
