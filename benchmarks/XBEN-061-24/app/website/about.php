<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - MLflow Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="index.php"><strong>MLflow Tracker</strong></a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="index.php">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="experiments.php">Experiments</a></li>
                    <li class="nav-item"><a class="nav-link" href="api-docs.php">API Docs</a></li>
                    <li class="nav-item"><a class="nav-link active" href="about.php">About</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container my-5">
        <h1 class="mb-4">About MLflow Tracker</h1>
        
        <div class="row">
            <div class="col-lg-8">
                <div class="card mb-4">
                    <div class="card-body">
                        <h2>What is MLflow?</h2>
                        <p>
                            MLflow is an open-source platform for managing the end-to-end machine learning lifecycle. 
                            It tackles four primary functions: tracking experiments, packaging code into reproducible runs, 
                            sharing and deploying models, and providing a central model registry.
                        </p>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-body">
                        <h2>Key Features</h2>
                        <ul>
                            <li><strong>Experiment Tracking</strong> - Record and compare parameters, metrics, and artifacts</li>
                            <li><strong>Model Packaging</strong> - Package models for reproducible deployment</li>
                            <li><strong>Model Registry</strong> - Centralized model store for collaboration</li>
                            <li><strong>REST API</strong> - Programmatic access to all tracking functionality</li>
                        </ul>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-body">
                        <h2>Version Information</h2>
                        <table class="table">
                            <tr>
                                <td><strong>Version</strong></td>
                                <td>2.10.2</td>
                            </tr>
                            <tr>
                                <td><strong>Backend Store</strong></td>
                                <td>file:///tmp/mlruns</td>
                            </tr>
                            <tr>
                                <td><strong>Artifact Root</strong></td>
                                <td>file:///tmp/mlruns/artifacts</td>
                            </tr>
                            <tr>
                                <td><strong>Build</strong></td>
                                <td>89a3c7f</td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>

            <div class="col-lg-4">
                <div class="card">
                    <div class="card-body">
                        <h5>Quick Links</h5>
                        <ul class="list-unstyled">
                            <li><a href="https://mlflow.org/docs/latest/index.html" target="_blank">Official Documentation</a></li>
                            <li><a href="https://github.com/mlflow/mlflow" target="_blank">GitHub Repository</a></li>
                            <li><a href="api-docs.php">API Reference</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container text-center">
            <p class="mb-0">&copy; 2024 MLflow Experiment Tracker</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
