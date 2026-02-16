<?php
$db = new mysqli('localhost', 'sc_admin', 'Cr@ftSecure2024', 'sitecraft');
if ($db->connect_error) {
    die("Connection failed: " . $db->connect_error);
}

$admin_hash = password_hash('admin123', PASSWORD_BCRYPT);
$editor_hash = password_hash('editor123', PASSWORD_BCRYPT);

$stmt = $db->prepare("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)");

$username = 'admin';
$email = 'admin@sitecraft.local';
$role = 'admin';
$stmt->bind_param("ssss", $username, $email, $admin_hash, $role);
$stmt->execute();

$username = 'editor';
$email = 'editor@sitecraft.local';
$role = 'editor';
$stmt->bind_param("ssss", $username, $email, $editor_hash, $role);
$stmt->execute();

$stmt->close();
$db->close();
echo "Users seeded successfully.\n";
?>
