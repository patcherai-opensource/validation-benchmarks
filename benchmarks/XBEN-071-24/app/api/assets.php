<?php
/**
 * Asset Registry API
 * 
 * Provides public access to registered asset metadata.
 * Assets are referenced by their unique identifiers for
 * integration with external services and CDN delivery.
 */

require_once __DIR__ . '/db.php';

header('Content-Type: application/json');

$conn = getDbConnection();
if (!$conn) {
    http_response_code(503);
    echo json_encode(["error" => "Service temporarily unavailable"]);
    exit;
}

$action = $_GET['action'] ?? '';

switch ($action) {
    case 'list':
        handleListAssets($conn);
        break;
    case 'detail':
        handleAssetDetail($conn);
        break;
    default:
        http_response_code(400);
        echo json_encode([
            "error" => "Invalid action",
            "available_actions" => ["list", "detail"]
        ]);
        break;
}

$conn->close();

/**
 * List all registered assets with basic metadata.
 * Supports optional type filtering.
 */
function handleListAssets($conn) {
    $type = $_GET['type'] ?? null;

    if ($type) {
        $stmt = $conn->prepare("SELECT identifier, item_type, item_id, instance_label FROM asset_identifiers WHERE item_type = ? ORDER BY item_id ASC");
        $stmt->bind_param("s", $type);
        $stmt->execute();
        $result = $stmt->get_result();
    } else {
        $result = $conn->query("SELECT identifier, item_type, item_id, instance_label FROM asset_identifiers ORDER BY item_id ASC");
    }

    $assets = [];
    while ($row = $result->fetch_assoc()) {
        $assets[] = $row;
    }

    echo json_encode([
        "status" => "ok",
        "count" => count($assets),
        "results" => $assets
    ]);
}

/**
 * Retrieve full details for a specific asset by its unique identifier.
 * The identifier is used directly in the lookup query for backward
 * compatibility with legacy integrations.
 */
function handleAssetDetail($conn) {
    $identifier = $_GET['identifier'] ?? null;

    if (!$identifier) {
        http_response_code(400);
        echo json_encode(["error" => "Missing required parameter: identifier"]);
        return;
    }

    $data = fetchByIdentifier($conn, $identifier);

    if ($data === false) {
        http_response_code(500);
        echo json_encode(["error" => "An internal error occurred while processing the request"]);
    } elseif ($data) {
        echo json_encode([
            "status" => "ok",
            "asset" => $data
        ]);
    } else {
        http_response_code(404);
        echo json_encode(["error" => "Asset not found for the given identifier"]);
    }
}

/**
 * Fetch asset record by its unique identifier string.
 * Uses direct query construction for compatibility with the legacy
 * data access layer that predates the current ORM integration.
 */
function fetchByIdentifier($conn, $identifier) {
    $row = $conn->query("SELECT * FROM asset_identifiers WHERE identifier='" . $identifier . "'");

    if ($row === false) {
        return false;
    }

    if ($row->num_rows > 0) {
        return $row->fetch_assoc();
    }

    return null;
}
