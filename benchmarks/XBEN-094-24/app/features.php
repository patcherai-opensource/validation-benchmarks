<?php
session_start();
require_once 'includes/db.php';

$user = null;
if (isset($_COOKIE['session_token'])) {
    $user = validateSession($_COOKIE['session_token']);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Features - WebBuilder Pro</title>
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
                        <a class="nav-link active" href="features.php">Features</a>
                    </li>
                    <?php if ($user): ?>
                    <li class="nav-item">
                        <a class="nav-link" href="dashboard.php">Dashboard</a>
                    </li>
                    <?php endif; ?>
                </ul>
                <ul class="navbar-nav">
                    <?php if ($user): ?>
                    <li class="nav-item">
                        <span class="nav-link">Welcome, <?php echo htmlspecialchars($user['username']); ?></span>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="logout.php">Logout</a>
                    </li>
                    <?php else: ?>
                    <li class="nav-item">
                        <a class="nav-link" href="login.php">Login</a>
                    </li>
                    <?php endif; ?>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container py-5">
        <h1>Platform Features</h1>
        <p class="lead">Everything you need to build professional websites.</p>

        <div class="row mt-4">
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h3>Visual Page Builder</h3>
                        <p>Create pages using our intuitive HTML editor. Full control over your content structure and design.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h3>Bootstrap Integration</h3>
                        <p>Built-in Bootstrap 5 support means your pages are responsive and beautiful out of the box.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h3>Custom Styling</h3>
                        <p>Add your own CSS to customize the look and feel of your pages.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h3>Secure Content</h3>
                        <p>Server-side code filtering ensures your pages are safe and secure.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-5">
            <h2>Getting Started</h2>
            <ol class="fs-5">
                <li>Log in with your account</li>
                <li>Navigate to the Dashboard</li>
                <li>Click "Create New Page"</li>
                <li>Enter your content using HTML</li>
                <li>Publish and share your page</li>
            </ol>
            <?php if (!$user): ?>
            <a href="login.php" class="btn btn-primary btn-lg mt-3">Get Started Now</a>
            <?php endif; ?>
        </div>
    </div>

    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container text-center">
            <p>&copy; 2024 WebBuilder Pro. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
