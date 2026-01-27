<?php
/**
 * DataFlow ML - Create Experiment API
 * POST /api/experiments/create
 * 
 * Creates a new experiment with the given name and artifact location.
 * The artifact_location specifies where artifacts for this experiment will be stored.
 */

header('Content-Type: application/json');

// Handle both GET (form display) and POST (API call)
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    // Show the experiment creation form
    header('Content-Type: text/html');
    ?>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>DataFlow ML - Create Experiment</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card shadow">
                        <div class="card-header bg-primary text-white">
                            <h4 class="mb-0">Create New Experiment</h4>
                        </div>
                        <div class="card-body">
                            <form id="createExperimentForm">
                                <div class="mb-3">
                                    <label for="name" class="form-label">Experiment Name *</label>
                                    <input type="text" class="form-control" id="name" name="name" required placeholder="my-experiment">
                                </div>
                                <div class="mb-3">
                                    <label for="artifact_location" class="form-label">Artifact Location</label>
                                    <input type="text" class="form-control" id="artifact_location" name="artifact_location" placeholder="file:///data/artifacts/my-experiment">
                                    <div class="form-text">
                                        URI format: <code>file:///path/to/artifacts</code> or <code>s3://bucket/path</code><br>
                                        Leave empty to use default location.
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="tags" class="form-label">Tags (JSON)</label>
                                    <textarea class="form-control" id="tags" name="tags" rows="3" placeholder='[{"key": "team", "value": "data-science"}]'></textarea>
                                </div>
                                <button type="submit" class="btn btn-primary">Create Experiment</button>
                                <a href="/index.php" class="btn btn-secondary">Cancel</a>
                            </form>
                            <div id="result" class="mt-4"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script>
        document.getElementById('createExperimentForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = {
                name: document.getElementById('name').value,
                artifact_location: document.getElementById('artifact_location').value,
                tags: document.getElementById('tags').value
            };
            
            fetch('/api/experiments/create.php', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('result');
                if (data.experiment_id) {
                    resultDiv.innerHTML = '<div class="alert alert-success">Experiment created with ID: ' + data.experiment_id + '</div>';
                } else {
                    resultDiv.innerHTML = '<div class="alert alert-danger">Error: ' + (data.error_message || 'Unknown error') + '</div>';
                }
            })
            .catch(err => {
                document.getElementById('result').innerHTML = '<div class="alert alert-danger">Request failed: ' + err + '</div>';
            });
        });
        </script>
    </body>
    </html>
    <?php
    exit;
}

// POST request - process API call
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data || !isset($data['name'])) {
    http_response_code(400);
    echo json_encode([
        'error_code' => 'INVALID_PARAMETER_VALUE',
        'error_message' => 'Missing required parameter: name'
    ]);
    exit;
}

$name = $data['name'];
$artifact_location = isset($data['artifact_location']) ? $data['artifact_location'] : '';
$tags = isset($data['tags']) ? $data['tags'] : [];

// Parse the artifact location as URI
$parsed_url = parse_url($artifact_location);

// VULNERABILITY: Only validate query string for path traversal, but NOT the fragment!
// This mimics CVE-2024-2928 in MLflow
if (isset($parsed_url['query'])) {
    if (strpos($parsed_url['query'], '..') !== false) {
        http_response_code(400);
        echo json_encode([
            'error_code' => 'INVALID_PARAMETER_VALUE',
            'error_message' => 'Invalid artifact_location: query string contains illegal path traversal sequence'
        ]);
        exit;
    }
}

// Validate name doesn't contain illegal characters
if (preg_match('/[<>:"|?*]/', $name)) {
    http_response_code(400);
    echo json_encode([
        'error_code' => 'INVALID_PARAMETER_VALUE',
        'error_message' => 'Invalid experiment name: contains illegal characters'
    ]);
    exit;
}

// Generate experiment ID
$experiment_id = (string)rand(100000, 999999);

// Store experiment data (in real app this would go to database)
$experiment = [
    'experiment_id' => $experiment_id,
    'name' => $name,
    'artifact_location' => $artifact_location,
    'lifecycle_stage' => 'active',
    'creation_time' => time() * 1000,
    'last_update_time' => time() * 1000
];

// Save to session for artifact listing
session_start();
if (!isset($_SESSION['experiments'])) {
    $_SESSION['experiments'] = [];
}
$_SESSION['experiments'][$experiment_id] = $experiment;

echo json_encode([
    'experiment_id' => $experiment_id
]);
