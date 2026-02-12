<?php

$mysql_hostname = "localhost";
$mysql_user = "faquser";
$mysql_password = 'faq_db_2024!';
$mysql_database = "phpmyfaq";

@$db_connect = mysqli_connect($mysql_hostname, $mysql_user, $mysql_password, $mysql_database);
if (!$db_connect) {
    http_response_code(503);
    die("Service temporarily unavailable");
}

?>
