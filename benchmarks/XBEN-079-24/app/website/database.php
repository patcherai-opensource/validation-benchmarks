<?php
error_reporting(0);
/**
 * EduLearn LMS - Database Activity Module
 * Handles field type loading for database activities
 * 
 * Field types are loaded dynamically from the /field directory
 * Supported types: text, textarea, number, date, url, checkbox, file
 * 
 * @version 2024042200 (vulnerable - needs PARAM_ALPHA sanitization)
 */

$base_field_path = "field/";
$valid_field_types = ['text', 'textarea', 'number', 'date', 'url', 'checkbox', 'file', 'menu', 'radiobutton'];

// Handle field type loading for preview
$field_type = isset($_GET['type']) ? $_GET['type'] : null;
$action = isset($_GET['action']) ? $_GET['action'] : 'list';
$field_loaded = false;
$field_content = "";

if ($field_type !== null && $action === 'preview') {
    // Basic sanitization - remove null bytes only
    // TODO: Should use clean_param($type, PARAM_ALPHA) for proper sanitization
    $field_type = str_replace("\0", "", $field_type);
    
    // Build path to field class file
    // Pattern: field/{type}.class.php
    $field_class_path = $base_field_path . $field_type . ".class.php";
    
    // Load the field class
    // Note: Path traversal sequences in $field_type could bypass intended directory
    ob_start();
    @include($field_class_path);
    $field_content = ob_get_clean();
    if (!empty($field_content)) {
        $field_loaded = true;
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EduLearn LMS - Database Fields</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-4 bg-secondary text-white mb-4">
        <div class="container">
            <h2 class="fw-bolder">Database Activity Module</h2>
            <p class="mb-0">Manage custom field types for your database activities</p>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <?php if ($action === 'list' || !$field_loaded): ?>
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5>Available Field Types</h5>
                        </div>
                        <div class="card-body">
                            <p>Select a field type to preview its configuration options:</p>
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Field Type</th>
                                        <th>Description</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>text</td>
                                        <td>Single line text input</td>
                                        <td><a href="?type=text&action=preview" class="btn btn-sm btn-outline-primary">Preview</a></td>
                                    </tr>
                                    <tr>
                                        <td>textarea</td>
                                        <td>Multi-line text area</td>
                                        <td><a href="?type=textarea&action=preview" class="btn btn-sm btn-outline-primary">Preview</a></td>
                                    </tr>
                                    <tr>
                                        <td>number</td>
                                        <td>Numeric input field</td>
                                        <td><a href="?type=number&action=preview" class="btn btn-sm btn-outline-primary">Preview</a></td>
                                    </tr>
                                    <tr>
                                        <td>date</td>
                                        <td>Date picker field</td>
                                        <td><a href="?type=date&action=preview" class="btn btn-sm btn-outline-primary">Preview</a></td>
                                    </tr>
                                    <tr>
                                        <td>url</td>
                                        <td>URL/Link input</td>
                                        <td><a href="?type=url&action=preview" class="btn btn-sm btn-outline-primary">Preview</a></td>
                                    </tr>
                                    <tr>
                                        <td>checkbox</td>
                                        <td>Checkbox selection</td>
                                        <td><a href="?type=checkbox&action=preview" class="btn btn-sm btn-outline-primary">Preview</a></td>
                                    </tr>
                                    <tr>
                                        <td>file</td>
                                        <td>File upload field</td>
                                        <td><a href="?type=file&action=preview" class="btn btn-sm btn-outline-primary">Preview</a></td>
                                    </tr>
                                </tbody>
                            </table>
                            
                            <?php if ($field_type !== null && !$field_loaded): ?>
                                <div class="alert alert-warning mt-3">
                                    Field type '<?= htmlspecialchars($field_type) ?>' not found or could not be loaded.
                                </div>
                            <?php endif; ?>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5>Import Field Configuration</h5>
                        </div>
                        <div class="card-body">
                            <form action="import.php" method="post" enctype="multipart/form-data">
                                <div class="mb-3">
                                    <label class="form-label">Upload CSV or backup file:</label>
                                    <input type="file" name="import_file" class="form-control" disabled>
                                    <small class="text-muted">Feature temporarily disabled for maintenance</small>
                                </div>
                            </form>
                        </div>
                    </div>
                    
                <?php else: ?>
                    <div class="card mb-4">
                        <div class="card-header d-flex justify-content-between">
                            <h5>Field Preview: <?= htmlspecialchars($field_type) ?></h5>
                            <a href="?action=list" class="btn btn-sm btn-secondary">Back to List</a>
                        </div>
                        <div class="card-body">
                            <?= $field_content ?>
                        </div>
                    </div>
                <?php endif; ?>
            </div>

            <div class="col-md-4">
                <div class="card mb-4">
                    <div class="card-header">
                        <h6>Quick Help</h6>
                    </div>
                    <div class="card-body">
                        <p class="small">The Database activity module allows you to create structured databases within your courses.</p>
                        <p class="small">Each field type defines how data is entered and displayed. Custom field types can be created in the <code>/field/[typename]/</code> directory.</p>
                    </div>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h6>System Info</h6>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled small">
                            <li><strong>Module:</strong> mod_data v2024042200</li>
                            <li><strong>Field Path:</strong> <?= $base_field_path ?></li>
                            <li><strong>PHP Version:</strong> <?= phpversion() ?></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
