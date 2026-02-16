<?php
session_start();
require_once __DIR__ . '/includes/config.php';

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $login = isset($_POST["login"]) ? trim($_POST["login"]) : '';
    $password = isset($_POST["password"]) ? $_POST["password"] : '';

    if (empty($login) || empty($password)) {
        header("Location: /?error=1");
        exit;
    }

    $conn = db_connect();
    if (!$conn) {
        header("Location: /?error=1");
        exit;
    }

    $stmt = $conn->prepare("SELECT id, login, pw, admin FROM users WHERE login = ? AND is_active = 1");
    $stmt->bind_param("s", $login);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        $user = $result->fetch_assoc();
        if (password_verify($password, $user['pw'])) {
            $_SESSION['user_id'] = $user['id'];
            $_SESSION['user_login'] = $user['login'];
            $_SESSION['is_admin'] = $user['admin'];
            $_SESSION['authenticated'] = true;
            header("Location: /dashboard.php");
            exit;
        }
    }

    $stmt->close();
    $conn->close();

    header("Location: /?error=1");
    exit;
}

header("Location: /");
exit;
