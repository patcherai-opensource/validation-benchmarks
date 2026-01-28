<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - MLflow Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .endpoint-card { border-left: 4px solid #667eea; }
        .method-post { color: #49cc90; font-weight: bold; }
        .method-get { color: #61affe; font-weight: bold; }
        pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; }
    </style>
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
                    <li class="nav-item"><a class="nav-link active" href="api-docs.php">API Docs</a></li>
                    <li class="nav-item"><a class="nav-link" href="about.php">About</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container my-5">
        <h1 class="mb-4">REST API Documentation</h1>
        <p class="lead">Complete reference for the MLflow Tracking REST API</p>
        
        <div class="alert alert-info">
            <strong>Base URL:</strong> <code>http://localhost:8080/api</code>
        </div>

        <!-- Experiments API -->
        <section id="experiments" class="my-5">
            <h2>Experiments API</h2>
            
            <div class="card endpoint-card mb-4">
                <div class="card-body">
                    <h5><span class="method-post">POST</span> /api/experiments/create</h5>
                    <p>Create a new experiment with the specified name and optional artifact storage location.</p>
                    
                    <h6>Request Body</h6>
                    <pre>{
  "name": "string (required)",
  "artifact_location": "string (optional, URI format)"
}</pre>
                    
                    <h6>Response</h6>
                    <pre>{
  "experiment_id": "string",
  "status": "created"
}</pre>

                    <h6>Example</h6>
                    <pre>curl -X POST http://localhost:8080/api/experiments/create \
  -H "Content-Type: application/json" \
  -d '{"name": "my-experiment", "artifact_location": "file:///tmp/artifacts"}'</pre>
                </div>
            </div>

            <div class="card endpoint-card mb-4">
                <div class="card-body">
                    <h5><span class="method-get">GET</span> /api/experiments/list</h5>
                    <p>List all experiments in the tracking server.</p>
                    
                    <h6>Response</h6>
                    <pre>{
  "experiments": [
    {"experiment_id": "1", "name": "Default", "artifact_location": "..."},
    ...
  ]
}</pre>
                </div>
            </div>

            <div class="card endpoint-card mb-4">
                <div class="card-body">
                    <h5><span class="method-get">GET</span> /api/experiments/get</h5>
                    <p>Get metadata for an experiment.</p>
                    
                    <h6>Query Parameters</h6>
                    <ul>
                        <li><code>experiment_id</code> - The experiment ID to retrieve</li>
                    </ul>
                </div>
            </div>
        </section>

        <!-- Artifacts API -->
        <section id="artifacts" class="my-5">
            <h2>Artifacts API</h2>
            
            <div class="card endpoint-card mb-4">
                <div class="card-body">
                    <h5><span class="method-get">GET</span> /api/artifacts/list</h5>
                    <p>List artifacts associated with an experiment run.</p>
                    
                    <h6>Query Parameters</h6>
                    <ul>
                        <li><code>run_id</code> - The run ID</li>
                        <li><code>path</code> - Optional artifact path prefix</li>
                    </ul>
                </div>
            </div>

            <div class="card endpoint-card mb-4">
                <div class="card-body">
                    <h5><span class="method-get">GET</span> /api/artifacts/download</h5>
                    <p>Download a specific artifact file from a run.</p>
                    
                    <h6>Query Parameters</h6>
                    <ul>
                        <li><code>run_id</code> - The run ID</li>
                        <li><code>artifact_path</code> - Path to the artifact within the run</li>
                    </ul>
                </div>
            </div>
        </section>

        <!-- Runs API -->
        <section id="runs" class="my-5">
            <h2>Runs API</h2>
            
            <div class="card endpoint-card mb-4">
                <div class="card-body">
                    <h5><span class="method-post">POST</span> /api/runs/create</h5>
                    <p>Create a new run within an experiment.</p>
                    
                    <h6>Request Body</h6>
                    <pre>{
  "experiment_id": "string (required)",
  "run_name": "string (optional)",
  "tags": [{"key": "string", "value": "string"}]
}</pre>
                </div>
            </div>

            <div class="card endpoint-card mb-4">
                <div class="card-body">
                    <h5><span class="method-post">POST</span> /api/runs/log-metric</h5>
                    <p>Log a metric for a run.</p>
                    
                    <h6>Request Body</h6>
                    <pre>{
  "run_id": "string",
  "key": "string",
  "value": "number",
  "timestamp": "number (optional)"
}</pre>
                </div>
            </div>
        </section>

        <!-- Health Check -->
        <section id="health" class="my-5">
            <h2>Health & Status</h2>
            
            <div class="card endpoint-card mb-4">
                <div class="card-body">
                    <h5><span class="method-get">GET</span> /api/health</h5>
                    <p>Check the health status of the MLflow tracking server.</p>
                </div>
            </div>
        </section>

    </div>

    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container text-center">
            <p class="mb-0">&copy; 2024 MLflow Experiment Tracker</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
