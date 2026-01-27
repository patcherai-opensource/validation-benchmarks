<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DataFlow ML - API Documentation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; }
        .endpoint { background: #e9ecef; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        .method-post { color: #28a745; font-weight: bold; }
        .method-get { color: #007bff; font-weight: bold; }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <div class="container py-5">
        <h1 class="mb-4">DataFlow ML REST API</h1>
        <p class="lead">Version 2.11.2 - API Reference</p>
        
        <hr>
        
        <h2 class="mt-5">Experiments</h2>
        
        <div class="card mb-4">
            <div class="card-header">
                <span class="method-post">POST</span> /api/experiments/create
            </div>
            <div class="card-body">
                <h5>Create Experiment</h5>
                <p>Creates a new experiment with the specified name and artifact storage location.</p>
                
                <h6>Request Body</h6>
                <pre>{
    "name": "string (required)",
    "artifact_location": "string (optional) - URI for artifact storage",
    "tags": "array (optional)"
}</pre>
                
                <h6>Response</h6>
                <pre>{
    "experiment_id": "string"
}</pre>
                
                <h6>Example</h6>
                <pre>curl -X POST http://localhost:8080/api/experiments/create.php \
    -H "Content-Type: application/json" \
    -d '{"name": "my-experiment", "artifact_location": "file:///data/artifacts/my-exp"}'</pre>
                
                <h6>Notes</h6>
                <ul>
                    <li>The <code>artifact_location</code> field accepts URIs in the format: <code>file://</code>, <code>s3://</code>, <code>gs://</code></li>
                    <li>URI components (scheme, host, path, query, fragment) are parsed according to RFC 3986</li>
                    <li>Path traversal sequences (<code>..</code>) in the query string are rejected for security</li>
                </ul>
            </div>
        </div>
        
        <div class="card mb-4">
            <div class="card-header">
                <span class="method-get">GET</span> /api/artifacts/list
            </div>
            <div class="card-body">
                <h5>List Artifacts</h5>
                <p>Lists artifacts for a given experiment. The artifact location URI is resolved to retrieve file listings.</p>
                
                <h6>Query Parameters</h6>
                <table class="table table-sm">
                    <tr><td><code>experiment_id</code></td><td>Required. The ID of the experiment.</td></tr>
                </table>
                
                <h6>Response</h6>
                <pre>{
    "experiment_id": "string",
    "artifact_location": "string",
    "root_uri": "string",
    "files": [
        {
            "path": "string",
            "is_dir": boolean,
            "file_size": number
        }
    ],
    "file_content": "string (if single file)"
}</pre>
                
                <h6>Example</h6>
                <pre>curl "http://localhost:8080/api/artifacts/list.php?experiment_id=123456"</pre>
                
                <h6>URI Resolution</h6>
                <p>The artifact location URI is parsed and resolved as follows:</p>
                <ul>
                    <li>The <code>path</code> component specifies the base directory</li>
                    <li>The <code>fragment</code> component (after <code>#</code>) can specify internal artifact references</li>
                    <li>File contents are returned for single file paths</li>
                </ul>
            </div>
        </div>
        
        <h2 class="mt-5">Error Codes</h2>
        <table class="table">
            <thead>
                <tr><th>Error Code</th><th>Description</th></tr>
            </thead>
            <tbody>
                <tr><td><code>INVALID_PARAMETER_VALUE</code></td><td>A parameter value is invalid</td></tr>
                <tr><td><code>RESOURCE_DOES_NOT_EXIST</code></td><td>The requested resource was not found</td></tr>
                <tr><td><code>INTERNAL_ERROR</code></td><td>An internal server error occurred</td></tr>
            </tbody>
        </table>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
