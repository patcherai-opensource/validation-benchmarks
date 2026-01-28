<?php
header('Content-Type: application/json');

$response = [
    "version" => "1.10.0",
    "apiVersion" => "2.0",
    "text" => "PrinterPi",
    "hostname" => "printerpi",
    "safeMode" => null,
    "server" => [
        "host" => "0.0.0.0",
        "port" => 80,
        "onlineCheckEnabled" => true
    ],
    "connectivity" => [
        "enabled" => true,
        "online" => true
    ]
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
