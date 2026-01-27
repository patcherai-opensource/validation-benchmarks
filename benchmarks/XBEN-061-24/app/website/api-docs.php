<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DataFlow ML Tracking Server | API Documentation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .code-block { background-color: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; }
        .endpoint-badge { font-size: 0.8rem; }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">API Documentation</h1>
                <p class="lead mb-0">REST API Reference for DataFlow ML Tracking Server</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                
                <!-- Experiments API -->
                <div class="card mb-4">
                    <div class="card-header">
                        <span class="badge bg-success endpoint-badge">POST</span>
                        <code>/api/experiments/create.php</code>
                    </div>
                    <div class="card-body">
                        <h5>Create Experiment</h5>
                        <p>Create a new experiment with the specified configuration.</p>
                        
                        <h6>Request Body</h6>
                        <div class="code-block mb-3">
{
    "name": "experiment_name",
    "artifact_location": "file:///path/to/artifacts"  // optional
}
                        </div>
                        
                        <h6>Example Request</h6>
                        <div class="code-block mb-3">
curl -X POST http://localhost:8080/api/experiments/create.php \
  -H "Content-Type: application/json" \
  -d '{"name": "my-experiment", "artifact_location": "file:///var/dataflow/artifacts/test"}'
                        </div>

                        <h6>Response</h6>
                        <div class="code-block">
{
    "experiment_id": "exp-a1b2c3d4",
    "name": "my-experiment",
    "artifact_location": "file:///var/dataflow/artifacts/test",
    "status": "CREATED"
}
                        </div>
                    </div>
                </div>

                <!-- Model Versions API -->
                <div class="card mb-4">
                    <div class="card-header">
                        <span class="badge bg-success endpoint-badge">POST</span>
                        <code>/api/model-versions/create.php</code>
                    </div>
                    <div class="card-body">
                        <h5>Create Model Version</h5>
                        <p>Register a new model version from a source location.</p>
                        
                        <h6>Request Body</h6>
                        <div class="code-block mb-3">
{
    "name": "model_name",
    "source": "file:///path/to/model",  // required
    "description": "Model description"   // optional
}
                        </div>
                        
                        <h6>Example Request</h6>
                        <div class="code-block mb-3">
curl -X POST http://localhost:8080/api/model-versions/create.php \
  -H "Content-Type: application/json" \
  -d '{"name": "my-model", "source": "file:///var/dataflow/models/v1"}'
                        </div>

                        <h6>Response</h6>
                        <div class="code-block">
{
    "name": "my-model",
    "version": 1,
    "source": "file:///var/dataflow/models/v1",
    "status": "READY"
}
                        </div>
                    </div>
                </div>

                <!-- Notes Section -->
                <div class="card mb-4">
                    <div class="card-header bg-info text-white">
                        Notes
                    </div>
                    <div class="card-body">
                        <ul>
                            <li>The <code>artifact_location</code> and <code>source</code> parameters accept file:// URIs for local storage</li>
                            <li>Query parameters in URIs are not supported and will be rejected</li>
                            <li>All endpoints return JSON responses</li>
                            <li>Authentication is not required for this development instance</li>
                        </ul>
                    </div>
                </div>

            </div>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
