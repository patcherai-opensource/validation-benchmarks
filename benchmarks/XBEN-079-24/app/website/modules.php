<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EduLearn LMS - Modules</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <? include("include/navigation-bar.php") ?>

    <header class="py-4 bg-info text-white mb-4">
        <div class="container">
            <h2 class="fw-bolder">Available Modules</h2>
            <p class="mb-0">Extend your LMS functionality with these modules</p>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="list-group mb-4">
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">Assignment Module</h5>
                            <span class="badge bg-success">Active</span>
                        </div>
                        <p class="mb-1">Create and manage student assignments with automatic grading.</p>
                        <small class="text-muted">Version 2024.04.15</small>
                    </div>
                    
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">Quiz Module</h5>
                            <span class="badge bg-success">Active</span>
                        </div>
                        <p class="mb-1">Build interactive quizzes with multiple question types.</p>
                        <small class="text-muted">Version 2024.03.22</small>
                    </div>
                    
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">Forum Module</h5>
                            <span class="badge bg-success">Active</span>
                        </div>
                        <p class="mb-1">Enable discussion forums for course collaboration.</p>
                        <small class="text-muted">Version 2024.02.10</small>
                    </div>
                    
                    <div class="list-group-item list-group-item-action">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">Database Module</h5>
                            <span class="badge bg-warning">Configured</span>
                        </div>
                        <p class="mb-1">Create structured data collections with custom field types.</p>
                        <small class="text-muted">Version 2024.04.22 | <a href="database.php">Configure →</a></small>
                    </div>
                    
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">Wiki Module</h5>
                            <span class="badge bg-secondary">Inactive</span>
                        </div>
                        <p class="mb-1">Collaborative wiki pages for course knowledge bases.</p>
                        <small class="text-muted">Version 2024.01.18</small>
                    </div>
                    
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">Gradebook Module</h5>
                            <span class="badge bg-success">Active</span>
                        </div>
                        <p class="mb-1">Track and calculate student grades automatically.</p>
                        <small class="text-muted">Version 2024.04.01</small>
                    </div>
                </div>
            </div>

            <? include("include/sidebar.php") ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
