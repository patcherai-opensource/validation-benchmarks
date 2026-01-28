<?php
/**
 * phpDocFAQ Database Configuration
 * Version 3.2.5
 */

$mysql_hostname = "localhost";
$mysql_user = "web_db_user";
$mysql_password = 'P@ssw0rd123!';
$mysql_database = "faq_db";

$db_connect = mysqli_connect($mysql_hostname, $mysql_user, $mysql_password, $mysql_database) or die("Could not connect database");

?>
