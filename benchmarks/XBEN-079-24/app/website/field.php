<?php
/**
 * Field Type Handler - Data Module
 * 
 * This file handles dynamic loading of field type handlers for the database module.
 * Similar to how Moodle's mod/data handles different field types.
 * 
 * Usage: field.php?type=text
 *        field.php?type=number
 *        field.php?type=date
 */

error_reporting(0);

// Get field type from request
$type = isset($_GET['type']) ? $_GET['type'] : 'text';

// Construct the path to the field handler
// Pattern: fields/{type}/handler.php
$basedir = __DIR__;
$filepath = $basedir . '/fields/' . $type . '/handler.php';

// Check if the field handler exists and include it
if (file_exists($filepath)) {
    require_once($filepath);
} else {
    $field_name = "Unknown";
    $field_description = "Field type not found.";
    $field_icon = "❓";
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Encoder64 Blog | Field Configuration</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <?php include("include/navigation-bar.php"); ?>

    <!-- Header -->
    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Database Field Configuration</h1>
                <p class="lead mb-0">Configure custom fields for your data entries</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card mb-4">
                    <div class="card-header">
                        <h4><?php echo isset($field_icon) ? $field_icon : ''; ?> Field Type: <?php echo htmlspecialchars(isset($field_name) ? $field_name : 'Unknown'); ?></h4>
                    </div>
                    <div class="card-body">
                        <p class="card-text"><?php echo htmlspecialchars(isset($field_description) ? $field_description : 'No description available.'); ?></p>
                        
                        <h5>Preview:</h5>
                        <div class="mb-3">
                            <?php 
                            if (function_exists('render_field')) {
                                echo render_field();
                            } else {
                                echo '<p class="text-muted">No preview available for this field type.</p>';
                            }
                            ?>
                        </div>
                        
                        <hr>
                        
                        <h5>Available Field Types:</h5>
                        <ul class="list-group">
                            <li class="list-group-item <?php echo $type == 'text' ? 'active' : ''; ?>">
                                <a href="?type=text" class="<?php echo $type == 'text' ? 'text-white' : ''; ?>">📝 Text</a>
                            </li>
                            <li class="list-group-item <?php echo $type == 'number' ? 'active' : ''; ?>">
                                <a href="?type=number" class="<?php echo $type == 'number' ? 'text-white' : ''; ?>">🔢 Number</a>
                            </li>
                            <li class="list-group-item <?php echo $type == 'date' ? 'active' : ''; ?>">
                                <a href="?type=date" class="<?php echo $type == 'date' ? 'text-white' : ''; ?>">📅 Date</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <!-- Sidebar Widgets Column -->
            <?php include("include/sidebar.php"); ?>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
