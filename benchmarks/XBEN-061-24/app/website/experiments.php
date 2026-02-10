<?php
error_reporting(0);

$experiments_file = '/var/lib/mltrack/experiments.json';
$data_dir = '/var/lib/mltrack';

if (!is_dir($data_dir)) {
    @mkdir($data_dir, 0755, true);
}

function load_experiments() {
    global $experiments_file;
    if (!file_exists($experiments_file)) {
        return [];
    }
    return json_decode(file_get_contents($experiments_file), true) ?: [];
}

function save_experiments($experiments) {
    global $experiments_file;
    file_put_contents($experiments_file, json_encode($experiments, JSON_PRETTY_PRINT));
}

function validate_artifact_location($location) {
    $parsed = parse_url($location);
    
    if ($parsed === false) {
        return ['valid' => false, 'error' => 'Invalid URL format'];
    }
    
    $scheme = isset($parsed['scheme']) ? $parsed['scheme'] : '';
    if (!in_array($scheme, ['file', 'http', 'https', 's3', 'gs', 'wasbs'])) {
        return ['valid' => false, 'error' => 'Unsupported scheme. Supported: file, http, https, s3, gs, wasbs'];
    }
    
    $path = isset($parsed['path']) ? $parsed['path'] : '';
    $query = isset($parsed['query']) ? $parsed['query'] : '';
    
    if (strpos($path, '..') !== false) {
        return ['valid' => false, 'error' => 'Path traversal detected in path component'];
    }
    
    if (strpos($query, '..') !== false) {
        return ['valid' => false, 'error' => 'Path traversal detected in query component'];
    }
    
    return ['valid' => true];
}

$action = isset($_GET['action']) ? $_GET['action'] : 'list';
$message = '';
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $content_type = isset($_SERVER['CONTENT_TYPE']) ? $_SERVER['CONTENT_TYPE'] : '';
    
    if (strpos($content_type, 'application/json') !== false) {
        $input = json_decode(file_get_contents('php://input'), true);
        $name = isset($input['name']) ? trim($input['name']) : '';
        $artifact_location = isset($input['artifact_location']) ? trim($input['artifact_location']) : '';
    } else {
        $name = isset($_POST['name']) ? trim($_POST['name']) : '';
        $artifact_location = isset($_POST['artifact_location']) ? trim($_POST['artifact_location']) : '';
    }
    
    if (empty($name)) {
        $error = 'Experiment name is required';
    } elseif (empty($artifact_location)) {
        $error = 'Artifact location is required';
    } else {
        $validation = validate_artifact_location($artifact_location);
        if (!$validation['valid']) {
            $error = $validation['error'];
        } else {
            $experiments = load_experiments();
            
            foreach ($experiments as $exp) {
                if ($exp['name'] === $name) {
                    $error = 'Experiment with this name already exists';
                    break;
                }
            }
            
            if (empty($error)) {
                $new_id = count($experiments) > 0 ? max(array_column($experiments, 'id')) + 1 : 1;
                
                $new_experiment = [
                    'id' => $new_id,
                    'name' => $name,
                    'artifact_location' => $artifact_location,
                    'created_at' => date('Y-m-d H:i:s'),
                    'lifecycle_stage' => 'active'
                ];
                
                $experiments[] = $new_experiment;
                save_experiments($experiments);
                
                if (strpos($content_type, 'application/json') !== false) {
                    header('Content-Type: application/json');
                    echo json_encode(['experiment_id' => $new_id]);
                    exit;
                }
                
                $message = "Experiment '{$name}' created successfully with ID: {$new_id}";
            }
        }
    }
    
    if (!empty($error) && strpos($content_type, 'application/json') !== false) {
        header('Content-Type: application/json');
        http_response_code(400);
        echo json_encode(['error' => $error]);
        exit;
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MLTrack - Create Experiment</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</head>
<body>
    <?php include("include/navigation-bar.php") ?>

    <header class="py-4 bg-light border-bottom mb-4">
        <div class="container">
            <h1 class="fw-bolder"><i class="bi bi-plus-circle"></i> Create New Experiment</h1>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <?php if (!empty($message)): ?>
                <div class="alert alert-success alert-dismissible fade show">
                    <i class="bi bi-check-circle"></i> <?= htmlspecialchars($message); ?>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
                <?php endif; ?>

                <?php if (!empty($error)): ?>
                <div class="alert alert-danger alert-dismissible fade show">
                    <i class="bi bi-exclamation-triangle"></i> <?= htmlspecialchars($error); ?>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
                <?php endif; ?>

                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Experiment Details</h5>
                    </div>
                    <div class="card-body">
                        <form method="post" action="experiments.php?action=create">
                            <div class="mb-3">
                                <label for="name" class="form-label">Experiment Name <span class="text-danger">*</span></label>
                                <input type="text" class="form-control" id="name" name="name" 
                                       value="<?= isset($_POST['name']) ? htmlspecialchars($_POST['name']) : ''; ?>"
                                       placeholder="my-ml-experiment" required>
                                <div class="form-text">A unique name for your experiment</div>
                            </div>

                            <div class="mb-3">
                                <label for="artifact_location" class="form-label">Artifact Location <span class="text-danger">*</span></label>
                                <input type="text" class="form-control" id="artifact_location" name="artifact_location"
                                       value="<?= isset($_POST['artifact_location']) ? htmlspecialchars($_POST['artifact_location']) : ''; ?>"
                                       placeholder="file:///var/lib/mltrack/artifacts/my-experiment" required>
                                <div class="form-text">
                                    URI for storing artifacts. Supported schemes: <code>file://</code>, <code>s3://</code>, <code>gs://</code>, <code>wasbs://</code>, <code>http://</code>, <code>https://</code>
                                </div>
                            </div>

                            <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                <a href="index.php" class="btn btn-secondary">Cancel</a>
                                <button type="submit" class="btn btn-primary">
                                    <i class="bi bi-plus-circle"></i> Create Experiment
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <div class="card mt-4">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-code-slash"></i> API Usage</h5>
                    </div>
                    <div class="card-body">
                        <p>You can also create experiments via the REST API:</p>
                        <pre class="bg-dark text-light p-3 rounded"><code>POST /api/experiments/create
Content-Type: application/json

{
    "name": "my-experiment",
    "artifact_location": "file:///var/lib/mltrack/artifacts/my-exp"
}</code></pre>
                    </div>
                </div>
            </div>

            <?php include("include/sidebar.php") ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>