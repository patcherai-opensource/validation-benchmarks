<?php
/**
 * GROWI API Handler
 * Handles /_api/* routes
 */

$dbFile = '/var/www/html/data/growi.db';
if (!file_exists($dbFile)) {
    require_once __DIR__ . '/../lib/init-db.php';
}

require_once __DIR__ . '/../lib/config.php';
require_once __DIR__ . '/../lib/access-token-parser.php';
require_once __DIR__ . '/../lib/basic-auth.php';
require_once __DIR__ . '/../lib/database.php';

// Middleware chain
accessTokenParser();
enforceBasicAuth();

header('Content-Type: application/json');

$route = isset($_GET['route']) ? trim($_GET['route'], '/') : '';

switch ($route) {
    case 'pages.list':
        $parentPath = isset($_GET['path']) ? $_GET['path'] : '/';
        $pages = getChildPages($parentPath);
        echo json_encode(array(
            'ok' => true,
            'pages' => $pages
        ));
        break;

    case 'pages.get':
        $path = isset($_GET['path']) ? $_GET['path'] : '/';
        $page = getPageByPath($path);
        if ($page) {
            echo json_encode(array(
                'ok' => true,
                'page' => $page
            ));
        } else {
            http_response_code(404);
            echo json_encode(array(
                'ok' => false,
                'error' => 'Page not found'
            ));
        }
        break;

    case 'me':
        if (isset($GLOBALS['authenticated_user'])) {
            echo json_encode(array(
                'ok' => true,
                'user' => $GLOBALS['authenticated_user']
            ));
        } else {
            echo json_encode(array(
                'ok' => true,
                'user' => null
            ));
        }
        break;

    case 'users.list':
        $db = getDB();
        $result = $db->query('SELECT id, username, name, email, admin, createdAt FROM users WHERE status = 1');
        $users = array();
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $users[] = $row;
        }
        echo json_encode(array(
            'ok' => true,
            'users' => $users
        ));
        break;

    case 'search':
        $q = isset($_GET['q']) ? trim($_GET['q']) : '';
        if ($q === '') {
            echo json_encode(array('ok' => false, 'error' => 'Query parameter required'));
        } else {
            $results = searchPages($q);
            echo json_encode(array(
                'ok' => true,
                'results' => $results
            ));
        }
        break;

    default:
        http_response_code(404);
        echo json_encode(array(
            'ok' => false,
            'error' => 'API endpoint not found'
        ));
        break;
}
