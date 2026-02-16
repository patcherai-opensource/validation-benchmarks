<?php

$mysql_hostname = "localhost";
$mysql_user = "kb_db_user";
$mysql_password = 'Kb$ecure2024!';
$mysql_database = "knowledgebase";

$db_connect = mysqli_connect($mysql_hostname, $mysql_user, $mysql_password, $mysql_database);
if (!$db_connect) {
    http_response_code(503);
    exit();
}
mysqli_set_charset($db_connect, "utf8mb4");

?>
