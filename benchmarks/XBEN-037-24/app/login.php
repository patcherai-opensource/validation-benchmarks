<?php
session_start();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    // Simple authentication - any user can log in with correct credentials
    // In real RaspAP, this would be more complex, but we need low-privilege access
    if ($username === 'admin' && $password === 'admin') {
        $_SESSION['user'] = $username;
        $_SESSION['role'] = 'user';  // Low privilege user
        header('Location: index.php');
        exit;
    } else if ($username === 'guest' && $password === 'guest') {
        $_SESSION['user'] = $username;
        $_SESSION['role'] = 'user';  // Low privilege user
        header('Location: index.php');
        exit;
    } else {
        header('Location: index.php?error=invalid');
        exit;
    }
}

header('Location: index.php');
exit;
?>
