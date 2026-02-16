<?php
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/db.php';
require_once __DIR__ . '/../includes/query_validator.php';

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

$user = get_session_user();
$is_api_call = (isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false) 
    || isset($_GET['format']) && $_GET['format'] === 'json';

// Check authentication and authorization
if (!$user) {
    if ($is_api_call) {
        http_response_code(401);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Authentication required. Please login first.']);
        exit;
    }
    header('Location: /login.php');
    exit;
}

if (!require_role('editor')) {
    if ($is_api_call) {
        http_response_code(403);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Insufficient permissions. Editor role or above required to use content query API.']);
        exit;
    }
    http_response_code(403);
    echo "Access denied. Editor role required.";
    exit;
}

$query_input = '';
$results = [];
$error = '';
$executed_query = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' || isset($_GET['q'])) {
    $query_input = $_POST['query'] ?? $_GET['q'] ?? '';
    
    if (!empty($query_input)) {
        // Complete the statement if it's in short form
        $complete_statement = to_complete_statement($query_input);
        
        // Validate the completed statement
        if (!is_query_safe($complete_statement)) {
            $error = 'Query validation failed. Only SELECT queries on wiki_documents and wiki_spaces tables are permitted.';
        } else {
            $conn = get_db_connection();
            if ($conn) {
                $executed_query = $complete_statement;
                $result = $conn->query($complete_statement);
                
                if ($result) {
                    while ($row = $result->fetch_assoc()) {
                        $results[] = $row;
                    }
                } else {
                    $error = 'Query execution error.';
                }
                $conn->close();
            } else {
                $error = 'Database connection unavailable.';
            }
        }
    }
}

// JSON response for API calls
if ($is_api_call) {
    header('Content-Type: application/json');
    if ($error) {
        http_response_code(400);
        echo json_encode(['error' => $error]);
    } else {
        echo json_encode([
            'results' => $results,
            'count' => count($results)
        ]);
    }
    exit;
}

// HTML response for browser access
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Query API - WikiEngine</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">WikiEngine</a>
            <span class="version">v3.8.2</span>
        </div>
        <div class="nav-links">
            <a href="/browse.php">Browse</a>
            <a href="/spaces.php">Spaces</a>
            <a href="/api/search_content.php" class="active">Content Query</a>
            <span class="nav-user"><?php echo htmlspecialchars($user['display_name']); ?> (<?php echo htmlspecialchars($user['role']); ?>)</span>
            <a href="/logout.php">Logout</a>
        </div>
    </nav>

    <div class="container">
        <h2>Content Query</h2>
        <p class="help-text">Execute queries against the wiki document store. Use short-form syntax (e.g., <code>where doc_space='Main'</code>) or provide complete SELECT statements. Only queries against <code>wiki_documents</code> and <code>wiki_spaces</code> are permitted.</p>
        
        <form method="POST" action="/api/search_content.php">
            <div class="form-group">
                <label for="query">Query</label>
                <textarea id="query" name="query" rows="3" class="form-control" placeholder="where doc_space='Main' order by doc_modified desc"><?php echo htmlspecialchars($query_input); ?></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Execute Query</button>
        </form>

        <?php if ($error): ?>
        <div class="alert alert-error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>

        <?php if (count($results) > 0): ?>
        <div class="results-section">
            <h3>Results (<?php echo count($results); ?> rows)</h3>
            <table class="doc-table">
                <thead>
                    <tr>
                        <?php foreach (array_keys($results[0]) as $key): ?>
                        <th><?php echo htmlspecialchars($key); ?></th>
                        <?php endforeach; ?>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($results as $row): ?>
                    <tr>
                        <?php foreach ($row as $val): ?>
                        <td><?php echo htmlspecialchars($val ?? ''); ?></td>
                        <?php endforeach; ?>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        <?php elseif ($_SERVER['REQUEST_METHOD'] === 'POST' && empty($error)): ?>
        <div class="results-section">
            <p>No results found.</p>
        </div>
        <?php endif; ?>
    </div>

    <footer class="footer">
        <p>WikiEngine Platform v3.8.2 &copy; 2024</p>
    </footer>
</body>
</html>
