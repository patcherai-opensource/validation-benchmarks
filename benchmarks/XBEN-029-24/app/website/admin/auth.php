<?php
session_start();

if (!isset($_SESSION['user_id']) || !isset($_SESSION['login'])) {
    header("Location: ../index.php");
    exit();
}

function hasRight($db, $user_id, $right_name) {
    $stmt = mysqli_prepare($db, "SELECT right_id FROM faquser_right WHERE user_id = ? AND right_name = ?");
    mysqli_stmt_bind_param($stmt, "is", $user_id, $right_name);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    $has = mysqli_num_rows($result) > 0;
    mysqli_stmt_close($stmt);
    return $has;
}
?>
