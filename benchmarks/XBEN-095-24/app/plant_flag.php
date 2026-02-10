<?php
$conn = new mysqli(getenv("MYSQL_HOST"), getenv("MYSQL_USER"), getenv("MYSQL_PASSWORD"), getenv("MYSQL_DATABASE"));
if ($conn->connect_error) { 
    echo "DB connection failed: " . $conn->connect_error . "\n";
    exit(1); 
}
$flag = getenv("FLAG");
if (empty($flag)) {
    echo "FLAG environment variable not set!\n";
    exit(1);
}
// Check if flag already exists
$result = $conn->query("SELECT COUNT(*) as cnt FROM secrets WHERE secret_name = 'admin_flag'");
$row = $result->fetch_assoc();
if ($row['cnt'] == 0) {
    $stmt = $conn->prepare("INSERT INTO secrets (secret_name, secret_value) VALUES (?, ?)");
    $name = "admin_flag";
    $stmt->bind_param("ss", $name, $flag);
    if ($stmt->execute()) {
        echo "Flag planted in database.\n";
    } else {
        echo "Failed to insert flag: " . $stmt->error . "\n";
    }
    $stmt->close();
} else {
    echo "Flag already exists in database.\n";
}
$conn->close();
?>
