<?php
session_start();
require_once __DIR__ . '/../includes/db.php';
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/query.php';

$current_user = require_login();
require_right($current_user, 'SCRIPT');

$conn = get_db_connection();
$query_service = new QueryManagerScriptService($conn);

$query_input = '';
$query_result = null;
$error_msg = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $script_content = isset($_POST['script']) ? $_POST['script'] : '';

    // Parse velocity-like script syntax to extract HQL query
    // Supports: $services.query.hql("...").execute()
    if (preg_match('/\$services\.query\.hql\(\s*"(.+?)"\s*\)\.execute\(\)/', $script_content, $matches)) {
        $query_input = $matches[1];
        $query_result = $query_service->hql($query_input);
    } elseif (preg_match('/\$services\.query\.hql\(\s*\'(.+?)\'\s*\)\.execute\(\)/', $script_content, $matches)) {
        $query_input = $matches[1];
        $query_result = $query_service->hql($query_input);
    } else {
        $error_msg = 'Unsupported script syntax. Use: $services.query.hql("your HQL query").execute()';
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XWiki - Script Console</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div id="xwikimaincontainer">
    <div id="xwikiheader">
        <div class="navbar">
            <a href="/" class="brand">XWiki Platform</a>
            <div class="nav-links">
                <a href="/bin/view/Main/">Wiki</a>
                <a href="/bin/view/Blog/">Blog</a>
                <a href="/bin/view/Sandbox/">Sandbox</a>
                <a href="/bin/view/XWiki/ScriptConsole" class="active">Script Console</a>
                <span class="user-info"><?php echo htmlspecialchars($current_user['XWU_USERNAME']); ?></span>
                <a href="/bin/logout">Logout</a>
            </div>
        </div>
    </div>

    <div id="xwikicontent" class="main-content">
        <h1>Script Console</h1>
        <p>Execute Velocity scripts with wiki query services. Requires <strong>SCRIPT</strong> right.</p>
        <p class="info-note">Note: Full HQL queries require PROGRAMMING right. Use short-form queries (e.g., <code>where ...</code>) with SCRIPT right.</p>

        <form method="POST" action="/bin/view/XWiki/ScriptConsole">
            <div class="form-group">
                <label for="script">Script Content (Velocity):</label>
                <textarea id="script" name="script" rows="6" class="code-input" placeholder="{{velocity}}&#10;$services.query.hql(&quot;where doc.XWD_AUTHOR = 'Admin'&quot;).execute()&#10;{{/velocity}}"><?php echo isset($_POST['script']) ? htmlspecialchars($_POST['script']) : ''; ?></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Execute</button>
        </form>

        <?php if ($error_msg): ?>
            <div class="message error"><?php echo htmlspecialchars($error_msg); ?></div>
        <?php endif; ?>

        <?php if ($query_result !== null): ?>
            <div class="result-section">
                <h2>Result</h2>
                <?php if (isset($query_result['error'])): ?>
                    <div class="message error"><?php echo htmlspecialchars($query_result['error']); ?></div>
                <?php elseif (isset($query_result['results'])): ?>
                    <p>Found <?php echo $query_result['count']; ?> result(s).</p>
                    <?php if ($query_result['count'] > 0): ?>
                        <table class="wiki-table">
                            <thead>
                                <tr>
                                    <?php foreach (array_keys($query_result['results'][0]) as $col): ?>
                                        <th><?php echo htmlspecialchars($col); ?></th>
                                    <?php endforeach; ?>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($query_result['results'] as $row): ?>
                                <tr>
                                    <?php foreach ($row as $val): ?>
                                        <td><?php echo htmlspecialchars($val ?? ''); ?></td>
                                    <?php endforeach; ?>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    <?php endif; ?>
                <?php endif; ?>
            </div>
        <?php endif; ?>

        <div class="content-section">
            <h2>Examples</h2>
            <div class="code-example">
                <p>List all pages by a specific author:</p>
                <code>$services.query.hql("where doc.XWD_AUTHOR = 'Admin'").execute()</code>
            </div>
            <div class="code-example">
                <p>List pages ordered by modification date:</p>
                <code>$services.query.hql("where doc.XWD_HIDDEN = 0 order by doc.XWD_DATE desc").execute()</code>
            </div>
        </div>
    </div>

    <div id="xwikifooter">
        <p>Powered by <a href="#">XWiki Platform</a> 16.4.5</p>
    </div>
</div>
</body>
</html>