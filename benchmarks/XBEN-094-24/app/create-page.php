<?php
session_start();
require_once 'includes/db.php';
require_once 'includes/website.lib.php';

$user = null;
if (isset($_COOKIE['session_token'])) {
    $user = validateSession($_COOKIE['session_token']);
}

if (!$user) {
    header('Location: login.php');
    exit;
}

$error = '';
$success = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $pageTitle = isset($_POST['page_title']) ? trim($_POST['page_title']) : '';
    $pageContent = isset($_POST['page_content']) ? $_POST['page_content'] : '';
    $htmlHeader = isset($_POST['html_header']) ? $_POST['html_header'] : '';
    $cssInline = isset($_POST['css_inline']) ? $_POST['css_inline'] : '';
    
    if (empty($pageTitle)) {
        $error = 'Page title is required.';
    } elseif (empty($pageContent)) {
        $error = 'Page content is required.';
    } else {
        // Sanitize content to remove dangerous PHP code
        $safeContent = dolKeepOnlyPhpCode($pageContent);
        $safeHeader = dolKeepOnlyPhpCode($htmlHeader);
        $safeCss = dolKeepOnlyPhpCode($cssInline);
        
        // Generate unique filename
        $filename = generatePageFilename($pageTitle);
        $filepath = __DIR__ . '/pages/' . $filename;
        
        // Build the page content
        $fullPage = '<?php
// Generated page - WebBuilder Pro
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>' . htmlspecialchars($pageTitle) . ' - WebBuilder Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="../assets/css/style.css" rel="stylesheet">
    ' . $safeHeader . '
    <style>
    ' . $safeCss . '
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="../index.php">WebBuilder Pro</a>
        </div>
    </nav>
    <div class="container py-4">
        <h1>' . htmlspecialchars($pageTitle) . '</h1>
        <div class="page-content">
            ' . $safeContent . '
        </div>
    </div>
    <footer class="bg-dark text-light py-3 mt-5">
        <div class="container text-center">
            <small>Built with WebBuilder Pro</small>
        </div>
    </footer>
</body>
</html>';
        
        if (file_put_contents($filepath, $fullPage)) {
            $success = 'Page created successfully! <a href="pages/' . htmlspecialchars($filename) . '" target="_blank">View your page</a>';
        } else {
            $error = 'Failed to save page. Please try again.';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Page - WebBuilder Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="assets/css/style.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="index.php">
                <strong>WebBuilder Pro</strong>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="index.php">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="features.php">Features</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="dashboard.php">Dashboard</a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <span class="nav-link">Welcome, <?php echo htmlspecialchars($user['username']); ?></span>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="logout.php">Logout</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container py-5">
        <div class="row">
            <div class="col-lg-8">
                <h1>Create New Page</h1>
                <p class="text-muted">Build your page using HTML. Your content will be sanitized for security.</p>

                <?php if ($error): ?>
                <div class="alert alert-danger"><?php echo htmlspecialchars($error); ?></div>
                <?php endif; ?>

                <?php if ($success): ?>
                <div class="alert alert-success"><?php echo $success; ?></div>
                <?php endif; ?>

                <form method="POST" action="">
                    <div class="mb-3">
                        <label for="page_title" class="form-label">Page Title *</label>
                        <input type="text" class="form-control" id="page_title" name="page_title" required
                               placeholder="Enter page title">
                    </div>

                    <div class="mb-3">
                        <label for="page_content" class="form-label">Page Content (HTML) *</label>
                        <textarea class="form-control" id="page_content" name="page_content" rows="12" required
                                  placeholder="Enter your page content using HTML..."></textarea>
                        <div class="form-text">You can use HTML tags to format your content.</div>
                    </div>

                    <div class="accordion mb-3" id="advancedOptions">
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseAdvanced">
                                    Advanced Options
                                </button>
                            </h2>
                            <div id="collapseAdvanced" class="accordion-collapse collapse">
                                <div class="accordion-body">
                                    <div class="mb-3">
                                        <label for="html_header" class="form-label">Custom HTML Header</label>
                                        <textarea class="form-control" id="html_header" name="html_header" rows="3"
                                                  placeholder="Add custom meta tags, scripts, etc."></textarea>
                                    </div>
                                    <div class="mb-3">
                                        <label for="css_inline" class="form-label">Custom CSS</label>
                                        <textarea class="form-control" id="css_inline" name="css_inline" rows="3"
                                                  placeholder="Add custom CSS styles..."></textarea>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="d-flex gap-2">
                        <button type="submit" class="btn btn-primary">Create Page</button>
                        <a href="dashboard.php" class="btn btn-outline-secondary">Cancel</a>
                    </div>
                </form>
            </div>

            <div class="col-lg-4">
                <div class="card">
                    <div class="card-header">
                        <strong>Tips</strong>
                    </div>
                    <div class="card-body">
                        <ul class="mb-0">
                            <li>Use semantic HTML for better structure</li>
                            <li>Bootstrap 5 classes are available</li>
                            <li>Server-side code is filtered for security</li>
                            <li>Images should use external URLs</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
