<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLflow Experiment Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 0;
        }
        .feature-card {
            transition: transform 0.3s;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="index.php">
                <strong>MLflow Tracker</strong>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="index.php">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="experiments.php">Experiments</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="api-docs.php">API Docs</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="about.php">About</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
        <div class="container text-center">
            <h1 class="display-4 fw-bold mb-3">MLflow Experiment Tracking Platform</h1>
            <p class="lead mb-4">Track, compare, and manage your machine learning experiments with ease</p>
            <p class="text-light">Version 2.10.2 | Build 89a3c7f</p>
        </div>
    </section>

    <!-- Features Section -->
    <div class="container my-5">
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card feature-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="bi bi-graph-up"></i> Experiment Tracking
                        </h5>
                        <p class="card-text">Log parameters, metrics, and artifacts for each experiment run. Keep a complete history of your ML development.</p>
                        <a href="experiments.php" class="btn btn-outline-primary">View Experiments</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card feature-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="bi bi-folder"></i> Artifact Storage
                        </h5>
                        <p class="card-text">Store models, datasets, and other files associated with your experiments in flexible storage locations.</p>
                        <a href="api-docs.php#artifacts" class="btn btn-outline-primary">Learn More</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card feature-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="bi bi-code-slash"></i> REST API
                        </h5>
                        <p class="card-text">Integrate MLflow tracking into your workflow with our comprehensive REST API for experiment management.</p>
                        <a href="api-docs.php" class="btn btn-outline-primary">API Documentation</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Quick Start Section -->
    <div class="container my-5">
        <div class="card bg-light">
            <div class="card-body">
                <h3 class="card-title">Quick Start</h3>
                <p class="card-text">Create your first experiment using our REST API:</p>
                <pre class="bg-dark text-light p-3 rounded"><code>curl -X POST http://localhost:8080/api/experiments/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-experiment",
    "artifact_location": "file:///tmp/mlflow/artifacts"
  }'</code></pre>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container text-center">
            <p class="mb-0">&copy; 2024 MLflow Experiment Tracker. Open Source ML Platform.</p>
            <small class="text-muted">Powered by MLflow 2.10.2</small>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
