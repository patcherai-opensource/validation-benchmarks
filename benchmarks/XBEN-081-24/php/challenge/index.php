<?php
    include 'user-profile.php';
    include 'config.php';
    include 'misc.php';

    session_start();

    // Redirect to the store front page
    header("Location: /store/");
    exit();
?>
