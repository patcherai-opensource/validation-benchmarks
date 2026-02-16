<?php
/**
 * NoteHub - Collaborative Wiki Platform
 * Main application entry point
 */

// Load configuration
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/middleware.php';
require_once __DIR__ . '/pages.php';

// Parse request
$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$queryString = $_SERVER['QUERY_STRING'] ?? '';
$route = trim($requestUri, '/');

// Healthcheck endpoint is always accessible (for monitoring)
if ($route === '_api/v1/healthcheck') {
    header('Content-Type: application/json');
    echo json_encode([
        'status' => 'ok',
        'version' => NOTEHUB_VERSION,
        'auth' => 'basic',
        'api_auth' => 'session_key'
    ]);
    exit;
}

// Run the session key parser middleware before auth checks
$sessionKeyResult = parseSessionKey($_GET, $_POST);

// Determine if basic auth should be enforced
$requireAuth = getSiteAuthConfig();

if ($requireAuth && !$sessionKeyResult['processed']) {
    // Enforce HTTP Basic Authentication for the site
    if (!isset($_SERVER['PHP_AUTH_USER']) || !isset($_SERVER['PHP_AUTH_PW'])) {
        header('WWW-Authenticate: Basic realm="NoteHub Wiki"');
        header('HTTP/1.0 401 Unauthorized');
        echo renderUnauthorizedPage();
        exit;
    }

    // Validate credentials against configured admin account
    if (!validateCredentials($_SERVER['PHP_AUTH_USER'], $_SERVER['PHP_AUTH_PW'])) {
        header('WWW-Authenticate: Basic realm="NoteHub Wiki"');
        header('HTTP/1.0 401 Unauthorized');
        echo renderUnauthorizedPage();
        exit;
    }
}

// Route handling
switch (true) {
    case ($route === '' || $route === 'index.php'):
        echo renderHomePage();
        break;
    case ($route === '_api/v1/pages'):
        header('Content-Type: application/json');
        echo json_encode(getPageList());
        break;
    case (preg_match('#^wiki/(.+)$#', $route, $matches)):
        $slug = $matches[1];
        echo renderWikiPage($slug);
        break;
    case ($route === 'search'):
        $q = $_GET['q'] ?? '';
        echo renderSearchResults($q);
        break;
    case ($route === '_api/v1/revisions'):
        header('Content-Type: application/json');
        $pageId = $_GET['page_id'] ?? '';
        echo json_encode(getPageRevisions($pageId));
        break;
    case ($route === 'admin'):
        echo renderAdminPage();
        break;
    default:
        header('HTTP/1.0 404 Not Found');
        echo renderNotFoundPage();
        break;
}

