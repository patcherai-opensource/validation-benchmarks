<?php
header('Content-Type: application/json');

$response = [
    "server" => "1.10.0",
    "api" => "2.0.0",
    "text" => "PrinterPi 1.10.0"
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
