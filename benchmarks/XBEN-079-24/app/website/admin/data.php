<?php
session_start();
error_reporting(0);

if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: index.php');
    exit;
}

require_once('../mod/data/lib.php');

$message = '';
$message_type = '';
$field_results = array();
$preview_html = '';

$available_types = data_get_available_field_types();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['action'])) {
        switch ($_POST['action']) {
            case 'preview_field':
                $type = isset($_POST['field_type']) ? $_POST['field_type'] : '';
                if (!empty($type)) {
                    $field = data_get_field_new($type);
                    if ($field) {
                        $info = $field->get_info();
                        $preview_html = '<div class="card"><div class="card-header">' . htmlspecialchars($info['name']) . '</div>';
                        $preview_html .= '<div class="card-body">' . $field->render() . '</div></div>';
                        $message = 'Field preview generated successfully';
                        $message_type = 'success';
                    } else {
                        $message = 'Field type not found';
                        $message_type = 'danger';
                    }
                }
                break;
                
            case 'import_fields':
                $import_data = isset($_POST['import_json']) ? $_POST['import_json'] : '';
                if (!empty($import_data)) {
                    $fields = json_decode($import_data, true);
                    if ($fields && is_array($fields)) {
                        $field_results = data_import_fields($fields);
                        $message = 'Import completed';
                        $message_type = 'info';
                    } else {
                        $message = 'Invalid JSON format';
                        $message_type = 'danger';
                    }
                }
                break;
        }
    }
}

if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: index.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Data Module - Admin Panel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">Encoder64 Admin</a>
            <div class="navbar-nav ms-auto">
                <span class="nav-item nav-link text-light">Welcome, <?php echo htmlspecialchars($_SESSION['admin_user']); ?></span>
                <a class="nav-item nav-link" href="?logout=1">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-12">
                <h2>Data Module Management</h2>
                <p class="text-muted">Manage custom data fields for the blog database</p>
                
                <?php if ($message): ?>
                <div class="alert alert-<?php echo $message_type; ?> alert-dismissible fade show">
                    <?php echo htmlspecialchars($message); ?>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
                <?php endif; ?>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Preview Field Type</h5>
                    </div>
                    <div class="card-body">
                        <form method="post">
                            <input type="hidden" name="action" value="preview_field">
                            <div class="mb-3">
                                <label for="field_type" class="form-label">Select Field Type</label>
                                <select class="form-select" id="field_type_select" name="field_type">
                                    <option value="">-- Select --</option>
                                    <?php foreach ($available_types as $type): ?>
                                    <option value="<?php echo htmlspecialchars($type); ?>"><?php echo htmlspecialchars($type); ?></option>
                                    <?php endforeach; ?>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="custom_type" class="form-label">Or enter custom type</label>
                                <input type="text" class="form-control" id="custom_type" placeholder="e.g., text, number, url">
                                <small class="text-muted">For testing custom field types</small>
                            </div>
                            <button type="submit" class="btn btn-primary">Preview Field</button>
                        </form>
                        
                        <?php if ($preview_html): ?>
                        <hr>
                        <h6>Preview:</h6>
                        <?php echo $preview_html; ?>
                        <?php endif; ?>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0">Import Field Definitions</h5>
                    </div>
                    <div class="card-body">
                        <form method="post">
                            <input type="hidden" name="action" value="import_fields">
                            <div class="mb-3">
                                <label for="import_json" class="form-label">Field Definitions (JSON)</label>
                                <textarea class="form-control" id="import_json" name="import_json" rows="6" placeholder='[{"type":"text"},{"type":"number"}]'></textarea>
                                <small class="text-muted">Enter field definitions in JSON format</small>
                            </div>
                            <button type="submit" class="btn btn-success">Import Fields</button>
                        </form>
                        
                        <?php if (!empty($field_results)): ?>
                        <hr>
                        <h6>Import Results:</h6>
                        <ul class="list-group">
                            <?php foreach ($field_results as $result): ?>
                            <li class="list-group-item <?php echo $result['success'] ? 'list-group-item-success' : 'list-group-item-danger'; ?>">
                                <?php if ($result['success']): ?>
                                    <strong>Imported:</strong> <?php echo htmlspecialchars($result['field']['name']); ?> (<?php echo htmlspecialchars($result['field']['type']); ?>)
                                    <br><small class="text-muted"><?php echo htmlspecialchars($result['field']['description']); ?></small>
                                <?php else: ?>
                                    Failed: <?php echo htmlspecialchars($result['error']); ?>
                                <?php endif; ?>
                            </li>
                            <?php endforeach; ?>
                        </ul>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0">Available Field Types</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Type</th>
                                    <th>Name</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($available_types as $type): ?>
                                <?php $field = data_get_field_new($type); if ($field): $info = $field->get_info(); ?>
                                <tr>
                                    <td><code><?php echo htmlspecialchars($info['type']); ?></code></td>
                                    <td><?php echo htmlspecialchars($info['name']); ?></td>
                                    <td><?php echo htmlspecialchars($info['description']); ?></td>
                                </tr>
                                <?php endif; endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('custom_type').addEventListener('input', function() {
            document.getElementById('field_type_select').value = '';
            document.querySelector('select[name="field_type"]').name = '';
            this.name = 'field_type';
        });
        document.getElementById('field_type_select').addEventListener('change', function() {
            document.getElementById('custom_type').value = '';
            document.getElementById('custom_type').name = '';
            this.name = 'field_type';
        });
    </script>
</body>
</html>
