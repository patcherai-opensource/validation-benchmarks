<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>MLTrack API Documentation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .endpoint-card { border-left: 4px solid #198754; margin-bottom: 1rem; }
        .method-get { background-color: #61affe; color: white; }
        .method-post { background-color: #49cc90; color: white; }
        code { background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
        pre { background-color: #2d2d2d; color: #f8f8f2; padding: 1rem; border-radius: 5px; }
    </style>
</head>
<body>
    <? include("../include/navigation-bar.php") ?>

    <header class="py-4 bg-dark text-white mb-4">
        <div class="container">
            <h1>MLTrack REST API</h1>
            <p class="lead">Version 2.0 - Experiment Tracking & Model Registry</p>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-9">
                <h3>Overview</h3>
                <p>The MLTrack REST API allows you to programmatically manage experiments, runs, and artifacts. All endpoints are accessible at <code>/api/2.0/mltrack/</code>.</p>

                <hr>

                <h3>Experiments</h3>
                
                <div class="card endpoint-card">
                    <div class="card-body">
                        <h5><span class="badge method-get">GET</span> /api/2.0/mltrack/experiments/list</h5>
                        <p>List all experiments in the tracking server.</p>
                        <h6>Response:</h6>
                        <pre>{"experiments": [{"experiment_id": "exp-001", "name": "...", ...}]}</pre>
                    </div>
                </div>

                <div class="card endpoint-card">
                    <div class="card-body">
                        <h5><span class="badge method-post">POST</span> /api/2.0/mltrack/experiments/create</h5>
                        <p>Create a new experiment with the specified name and artifact location.</p>
                        <h6>Request Body:</h6>
                        <pre>{
  "name": "my-experiment",
  "artifact_location": "file:///path/to/artifacts"
}</pre>
                        <h6>Response:</h6>
                        <pre>{"experiment_id": "exp-007"}</pre>
                    </div>
                </div>

                <hr>

                <h3>Artifacts</h3>

                <div class="card endpoint-card">
                    <div class="card-body">
                        <h5><span class="badge method-get">GET</span> /api/2.0/mltrack/artifacts/list</h5>
                        <p>List artifacts at a given path.</p>
                        <h6>Query Parameters:</h6>
                        <ul>
                            <li><code>run_id</code> - ID of the run</li>
                            <li><code>path</code> - Path within artifact root</li>
                        </ul>
                    </div>
                </div>

                <div class="card endpoint-card">
                    <div class="card-body">
                        <h5><span class="badge method-get">GET</span> /api/2.0/mltrack/artifacts/get</h5>
                        <p>Download an artifact file.</p>
                        <h6>Query Parameters:</h6>
                        <ul>
                            <li><code>run_id</code> - ID of the run</li>
                            <li><code>path</code> - Path to the artifact</li>
                        </ul>
                    </div>
                </div>

                <hr>

                <h3>Model Registry</h3>

                <div class="card endpoint-card">
                    <div class="card-body">
                        <h5><span class="badge method-post">POST</span> /api/2.0/mltrack/model-versions/create</h5>
                        <p>Create a new model version from an existing artifact source.</p>
                        <h6>Request Body:</h6>
                        <pre>{
  "name": "my-model",
  "source": "file:///path/to/model/artifacts"
}</pre>
                        <h6>Response:</h6>
                        <pre>{"model_version": {"name": "my-model", "version": "1", ...}}</pre>
                    </div>
                </div>

                <div class="card endpoint-card">
                    <div class="card-body">
                        <h5><span class="badge method-get">GET</span> /api/2.0/mltrack/model-versions/get-download-uri</h5>
                        <p>Get the download URI for model version artifacts.</p>
                        <h6>Query Parameters:</h6>
                        <ul>
                            <li><code>name</code> - Model name</li>
                            <li><code>version</code> - Model version</li>
                        </ul>
                    </div>
                </div>

                <hr>
                
                <h3>Internal Endpoints</h3>
                <p class="text-muted">The following endpoints are for internal use:</p>
                <ul>
                    <li><code>/api/2.0/mltrack/artifacts/download</code> - Direct artifact download</li>
                    <li><code>/api/2.0/mltrack/preview-artifact</code> - Preview artifact contents</li>
                </ul>
                
            </div>
            <div class="col-md-3">
                <div class="card">
                    <div class="card-header">Quick Links</div>
                    <div class="card-body">
                        <ul class="list-unstyled">
                            <li><a href="/index.php">Dashboard</a></li>
                            <li><a href="/models.php">Model Registry</a></li>
                            <li><a href="https://mltrack-docs.io">Full Documentation</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
