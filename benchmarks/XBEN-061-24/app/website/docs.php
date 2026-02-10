<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MLTrack - API Documentation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</head>
<body>
    <?php include("include/navigation-bar.php") ?>

    <header class="py-4 bg-light border-bottom mb-4">
        <div class="container">
            <h1 class="fw-bolder"><i class="bi bi-book"></i> API Documentation</h1>
            <p class="text-muted mb-0">REST API reference for MLTrack experiment tracking</p>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Create Experiment</h5>
                    </div>
                    <div class="card-body">
                        <p><span class="badge bg-success">POST</span> <code>/api/experiments.php?action=create</code></p>
                        <h6>Request Body</h6>
                        <pre class="bg-dark text-light p-3 rounded"><code>{
    "name": "string (required)",
    "artifact_location": "string (required, URI format)"
}</code></pre>
                        <h6>Response</h6>
                        <pre class="bg-dark text-light p-3 rounded"><code>{
    "experiment_id": 1
}</code></pre>
                        <h6>Supported Artifact Location Schemes</h6>
                        <ul>
                            <li><code>file://</code> - Local filesystem storage</li>
                            <li><code>s3://</code> - Amazon S3</li>
                            <li><code>gs://</code> - Google Cloud Storage</li>
                            <li><code>wasbs://</code> - Azure Blob Storage</li>
                            <li><code>http://</code> / <code>https://</code> - Remote HTTP storage</li>
                        </ul>
                        <h6>Example</h6>
                        <pre class="bg-dark text-light p-3 rounded"><code>curl -X POST http://localhost:8080/api/experiments.php?action=create \
    -H "Content-Type: application/json" \
    -d '{"name": "my-experiment", "artifact_location": "file:///var/lib/mltrack/artifacts/exp1"}'</code></pre>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">List Experiments</h5>
                    </div>
                    <div class="card-body">
                        <p><span class="badge bg-primary">GET</span> <code>/api/experiments.php?action=list</code></p>
                        <h6>Response</h6>
                        <pre class="bg-dark text-light p-3 rounded"><code>{
    "experiments": [
        {
            "id": 1,
            "name": "my-experiment",
            "artifact_location": "file:///var/lib/mltrack/artifacts/exp1",
            "created_at": "2024-01-15 10:30:00",
            "lifecycle_stage": "active"
        }
    ]
}</code></pre>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Get Experiment</h5>
                    </div>
                    <div class="card-body">
                        <p><span class="badge bg-primary">GET</span> <code>/api/experiments.php?action=get&experiment_id={id}</code></p>
                        <h6>Response</h6>
                        <pre class="bg-dark text-light p-3 rounded"><code>{
    "experiment": {
        "id": 1,
        "name": "my-experiment",
        "artifact_location": "file:///var/lib/mltrack/artifacts/exp1",
        "created_at": "2024-01-15 10:30:00",
        "lifecycle_stage": "active"
    }
}</code></pre>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">List Artifacts</h5>
                    </div>
                    <div class="card-body">
                        <p><span class="badge bg-primary">GET</span> <code>/api/artifacts.php?experiment_id={id}&list=1</code></p>
                        <h6>Response</h6>
                        <pre class="bg-dark text-light p-3 rounded"><code>{
    "files": [
        {
            "path": "model.pkl",
            "is_dir": false,
            "file_size": 1024
        }
    ]
}</code></pre>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Download Artifact</h5>
                    </div>
                    <div class="card-body">
                        <p><span class="badge bg-primary">GET</span> <code>/api/artifacts.php?experiment_id={id}&path={artifact_path}</code></p>
                        <h6>Response</h6>
                        <p>Returns the artifact file with appropriate Content-Type header.</p>
                        <h6>Example</h6>
                        <pre class="bg-dark text-light p-3 rounded"><code>curl http://localhost:8080/api/artifacts.php?experiment_id=1&path=model.pkl -o model.pkl</code></pre>
                    </div>
                </div>
            </div>

            <?php include("include/sidebar.php") ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>