<?php

if (NETCFG_AUTH_ENABLED) {
    $user = $_SERVER['PHP_AUTH_USER'] ?? '';
    $pass = $_SERVER['PHP_AUTH_PW'] ?? '';

    $validUser = 'admin';
    $validPass = 'secret';

    if ($user !== $validUser || $pass !== $validPass) {
        header('WWW-Authenticate: Basic realm="NetGate Administration"');
        header('HTTP/1.0 401 Unauthorized');
        echo 'Authentication required.';
        exit;
    }
}
