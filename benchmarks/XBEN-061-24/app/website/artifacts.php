<?php
error_reporting(0);

$experiments_file = '/var/lib/mltrack/experiments.json';

function load_experiments() {
    global $experiments_file;
    if (!file_exists($experiments_file)) {
        return [];
    }
    return json_decode(file_get_contents($experiments_file), true) ?: [];
}

function resolve_artifact_path($artifact_location, $artifact_path = '') {
    $parsed = parse_url($artifact_location);
    
    $base_path = isset($parsed['path']) ? $parsed['path'] : '';
    $fragment = isset($parsed['fragment']) ? $parsed['fragment'] : '';
    
    if (!empty($fragment)) {
        $resolved = $base_path . '/' . $fragment;
    } else {
        $resolved = $base_path;
    }
    
    if (!empty($artifact_path)) {
        $resolved = $resolved . '/' . $artifact_path;
    }
    
    $resolved = preg_replace('#/+#', '/', $resolved);
    
    return $resolved;
}

$experiment_id = isset($_GET['experiment_id']) ? (int)$_GET['experiment_id'] : 0;
$artifact_path = isset($_GET['path']) ? $_GET['path'] : '';
$download = isset($_GET['download']) && $_GET['download'] === '1';

$experiments = load_experiments();
$experiment = null;

foreach ($experiments as $exp) {
    if ($exp['id'] === $experiment_id) {
        $experiment = $exp;
        break;
    }
}

if ($experiment === null) {
    if (isset($_GET['download'])) {
        http_response_code(404);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Experiment not found']);
        exit;
    }
}

if ($download && $experiment !== null) {
    $resolved_path = resolve_artifact_path($experiment['artifact_location'], $artifact_path);
    
    if (file_exists($resolved_path) && is_file($resolved_path)) {
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename="' . basename($resolved_path) . '"');
        header('Content-Length: ' . filesize($resolved_path));
        readfile($resolved_path);
        exit;
    } else {
        http_response_code(404);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Artifact not found']);
        exit;
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MLTrack - Artifacts</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</head>
<body>
    <?php include("include/navigation-bar.php") ?>

    <header class="py-4 bg-light border-bottom mb-4">
        <div class="container">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb mb-0">
                    <li class="breadcrumb-item"><a href="index.php">Experiments</a></li>
                    <?php if ($experiment): ?>
                    <li class="breadcrumb-item active"><?= htmlspecialchars($experiment['name']); ?></li>
                    <?php else: ?>
                    <li class="breadcrumb-item active">Not Found</li>
                    <?php endif; ?>
                </ol>
            </nav>
            <h1 class="fw-bolder mt-2"><i class="bi bi-folder"></i> Artifacts</h1>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <?php if ($experiment === null): ?>
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i> Experiment not found. Please select a valid experiment.
                </div>
                <a href="index.php" class="btn btn-primary">Back to Experiments</a>
                <?php else: ?>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Experiment Details</h5>
                    </div>
                    <div class="card-body">
                        <dl class="row mb-0">
                            <dt class="col-sm-3">ID</dt>
                            <dd class="col-sm-9"><code><?= htmlspecialchars($experiment['id']); ?></code></dd>
                            
                            <dt class="col-sm-3">Name</dt>
                            <dd class="col-sm-9"><?= htmlspecialchars($experiment['name']); ?></dd>
                            
                            <dt class="col-sm-3">Artifact Location</dt>
                            <dd class="col-sm-9"><code><?= htmlspecialchars($experiment['artifact_location']); ?></code></dd>
                            
                            <dt class="col-sm-3">Created</dt>
                            <dd class="col-sm-9"><?= htmlspecialchars($experiment['created_at']); ?></dd>
                        </dl>
                    </div>
                </div>

                <?php
                $resolved_base = resolve_artifact_path($experiment['artifact_location']);
                $artifacts = [];
                if (is_dir($resolved_base)) {
                    $files = scandir($resolved_base);
                    foreach ($files as $file) {
                        if ($file !== '.' && $file !== '..') {
                            $full_path = $resolved_base . '/' . $file;
                            $artifacts[] = [
                                'name' => $file,
                                'type' => is_dir($full_path) ? 'directory' : 'file',
                                'size' => is_file($full_path) ? filesize($full_path) : '-'
                            ];
                        }
                    }
                }
                ?>

                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Artifact Browser</h5>
                        <span class="badge bg-secondary"><?= count($artifacts); ?> items</span>
                    </div>
                    <div class="card-body">
                        <?php if (empty($artifacts)): ?>
                        <div class="text-center text-muted py-4">
                            <i class="bi bi-folder2-open" style="font-size: 3rem;"></i>
                            <p class="mt-2">No artifacts found in this experiment.</p>
                            <p class="small">Artifacts will appear here when you log them via the API.</p>
                        </div>
                        <?php else: ?>
                        <table class="table table-hover mb-0">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Type</th>
                                    <th>Size</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($artifacts as $artifact): ?>
                                <tr>
                                    <td>
                                        <?php if ($artifact['type'] === 'directory'): ?>
                                        <i class="bi bi-folder text-warning"></i>
                                        <?php else: ?>
                                        <i class="bi bi-file-earmark text-secondary"></i>
                                        <?php endif; ?>
                                        <?= htmlspecialchars($artifact['name']); ?>
                                    </td>
                                    <td><?= $artifact['type']; ?></td>
                                    <td><?= is_numeric($artifact['size']) ? number_format($artifact['size']) . ' bytes' : $artifact['size']; ?></td>
                                    <td>
                                        <?php if ($artifact['type'] === 'file'): ?>
                                        <a href="artifacts.php?experiment_id=<?= $experiment['id']; ?>&path=<?= urlencode($artifact['name']); ?>&download=1" 
                                           class="btn btn-sm btn-outline-primary">
                                            <i class="bi bi-download"></i> Download
                                        </a>
                                        <?php endif; ?>
                                    </td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                        <?php endif; ?>
                    </div>
                </div>

                <div class="card mt-4">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-code-slash"></i> API Usage</h5>
                    </div>
                    <div class="card-body">
                        <p>Download artifacts via API:</p>
                        <pre class="bg-dark text-light p-3 rounded"><code>GET /artifacts.php?experiment_id=<?= $experiment['id']; ?>&path=model.pkl&download=1</code></pre>
                    </div>
                </div>

                <?php endif; ?>
            </div>

            <?php include("include/sidebar.php") ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>