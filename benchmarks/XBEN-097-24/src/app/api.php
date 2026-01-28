<?php
/**
 * OpenKnowledge Wiki - API Endpoint
 * Simple REST API for wiki operations
 */

header('Content-Type: application/json');

$action = isset($_GET['action']) ? $_GET['action'] : '';
$page = isset($_GET['page']) ? $_GET['page'] : '';

// Simulated page data
$pages = array(
    'HomePage' => array(
        'title' => 'Welcome to OpenKnowledge Wiki',
        'content' => 'OpenKnowledge is a collaborative documentation platform for teams.',
        'author' => 'admin',
        'modified' => '2024-12-15'
    ),
    'Documentation' => array(
        'title' => 'Documentation',
        'content' => 'This wiki supports various formatting options, themes, and templates.',
        'author' => 'admin',
        'modified' => '2024-12-10'
    )
);

switch ($action) {
    case 'list':
        echo json_encode(array(
            'status' => 'success',
            'pages' => array_keys($pages)
        ));
        break;
        
    case 'get':
        if (isset($pages[$page])) {
            echo json_encode(array(
                'status' => 'success',
                'page' => $pages[$page]
            ));
        } else {
            http_response_code(404);
            echo json_encode(array(
                'status' => 'error',
                'message' => 'Page not found'
            ));
        }
        break;
        
    case 'themes':
        echo json_encode(array(
            'status' => 'success',
            'themes' => array('default', 'classic', 'minimal'),
            'note' => 'Use theme parameter in wiki.php to switch themes'
        ));
        break;
        
    case 'version':
        echo json_encode(array(
            'status' => 'success',
            'version' => '2.4.1',
            'php_version' => phpversion(),
            'platform' => 'OpenKnowledge Wiki'
        ));
        break;
        
    default:
        echo json_encode(array(
            'status' => 'success',
            'message' => 'OpenKnowledge API v1.0',
            'endpoints' => array(
                'list' => 'List all pages',
                'get' => 'Get page content (requires page parameter)',
                'themes' => 'List available themes',
                'version' => 'Get version info'
            )
        ));
}
?>
