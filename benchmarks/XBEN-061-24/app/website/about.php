<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>MLTrack | About</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-5 bg-dark text-white mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">About MLTrack</h1>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="container mt-3">
                    <h1>Open Source ML Experiment Tracking</h1>
                    <p>
                        MLTrack is an open-source platform for managing the end-to-end machine learning lifecycle. 
                        It helps data scientists and ML engineers track experiments, package code into reproducible runs, 
                        and share and deploy models.
                    </p>

                    <h2>Key Features</h2>
                    <ul>
                        <li><strong>Experiment Tracking:</strong> Record and compare parameters, metrics, and artifacts across all your experiments.</li>
                        <li><strong>Model Registry:</strong> Centralized model store for managing the full lifecycle of ML models.</li>
                        <li><strong>Artifact Storage:</strong> Store and version datasets, models, and other artifacts with flexible backends.</li>
                        <li><strong>REST API:</strong> Full-featured API for programmatic access to all MLTrack functionality.</li>
                    </ul>

                    <h2>Architecture</h2>
                    <p>
                        MLTrack uses a tracking server that records experiments and serves the web UI. 
                        Artifacts can be stored locally using <code>file://</code> URIs or on cloud storage like S3 and GCS.
                    </p>
                    
                    <h2>Version Information</h2>
                    <p>
                        <strong>MLTrack Server:</strong> v2.9.2<br>
                        <strong>API Version:</strong> 2.0<br>
                        <strong>Backend:</strong> Local File Storage
                    </p>

                    <h2>Getting Started</h2>
                    <p>
                        Check out our <a href="/api/docs.php">API Documentation</a> to learn how to interact with the MLTrack server programmatically.
                        The REST API supports creating experiments, logging metrics, and managing artifacts.
                    </p>
                </div>
            </div>
            <!-- Sidebar Widgets Column -->
            <? include("include/sidebar.php") ?>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
