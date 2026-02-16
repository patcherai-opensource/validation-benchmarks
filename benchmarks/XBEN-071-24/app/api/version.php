<?php
/**
 * Version / health endpoint
 */

header('Content-Type: application/json');

echo json_encode([
    "application" => "ContentHub CMS",
    "api_version" => "1.4.2",
    "status" => "running",
    "endpoints" => [
        "/api/version.php" => "System version and health",
        "/api/assets.php?action=list" => "List registered assets",
        "/api/assets.php?action=detail&identifier=<id>" => "Get asset details by identifier",
        "/api/settings.php?scope=public" => "Public configuration settings"
    ]
]);
