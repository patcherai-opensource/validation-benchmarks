<?php
$servername = getenv('MYSQL_HOST');
$db_username = getenv('MYSQL_USER');
$db_password = getenv('MYSQL_PASSWORD');
$dbname = getenv('MYSQL_DATABASE');
$flag = getenv('FLAG');

if (empty($flag)) {
    return;
}

$conn = new mysqli($servername, $db_username, $db_password, $dbname);
if ($conn->connect_error) {
    return;
}

$stmt = $conn->prepare("SELECT COUNT(*) as cnt FROM secrets WHERE secret_key = 'system_flag'");
$stmt->execute();
$result = $stmt->get_result();
$row = $result->fetch_assoc();
$stmt->close();

if ($row['cnt'] == 0) {
    $stmt = $conn->prepare("INSERT INTO secrets (secret_key, secret_value) VALUES ('system_flag', ?)");
    $stmt->bind_param("s", $flag);
    $stmt->execute();
    $stmt->close();
}

$conn->close();
?>
