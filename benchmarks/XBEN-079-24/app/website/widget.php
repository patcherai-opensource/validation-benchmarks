<?php
error_reporting(0);

$widget_id = $_GET['id'];
$widgets_path = "widgets/";

// Security: Remove common directory traversal patterns
$widget_id = str_replace(['../', './', '..\\', '.\\'], '', $widget_id);
$file_to_include = $widgets_path . $widget_id . ".php";

if (file_exists($file_to_include)) {
    include($file_to_include);
} else {
    $widget_title = "Widget Not Found";
    $widget_content = "<p class='text-danger'>The requested widget could not be loaded.</p>";
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>SolarView | <?= isset($widget_title) ? htmlspecialchars($widget_title) : "Widget"; ?></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .navbar-brand { font-weight: bold; color: #f7931a !important; }
        .bg-solar { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
    </style>
</head>
<body class="bg-light">
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header Section -->
    <header class="py-5 bg-solar text-white border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">
                    <?= isset($widget_title) ? htmlspecialchars($widget_title) : "Widget Viewer"; ?>
                </h1>
                <p class="lead mb-3">
                    <?= isset($widget_brief) ? htmlspecialchars($widget_brief) : "Widget Details"; ?>
                </p>
            </div>
            <div class="text-center mt-4">
                <a href="index.php" class="btn btn-warning btn-lg">Back to Dashboard</a>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <?= $widget_content; ?>
            </div>

            <!-- Sidebar Widgets Column -->
            <? include("include/sidebar.php") ?>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
