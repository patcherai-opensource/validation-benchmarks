<?php
// SolarView Dashboard - Widget Analytics Platform
// Read the JSON file for widgets
$json_data = file_get_contents('widgets.json');
$widgets = json_decode($json_data, true);

// Define how many widgets per page
$limit = 5;

// Get the current page number
$page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$total_widgets = count($widgets);
$total_pages = ceil($total_widgets / $limit);
$start = ($page - 1) * $limit;
$end = $start + $limit;

// Slice the widgets array to get the widgets for the current page
$display_widgets = array_slice($widgets, $start, $limit);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>SolarView Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .navbar-brand { font-weight: bold; color: #f7931a !important; }
        .bg-solar { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
        .text-solar { color: #f7931a; }
    </style>
</head>
<body class="bg-light">
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header Section -->
    <header class="py-5 bg-solar text-white border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">SolarView Dashboard</h1>
                <p class="lead mb-0">Interactive Widget Analytics Platform v1.34.2</p>
                <small class="text-muted">Powered by widgetti framework</small>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <!-- Widget Entries Column -->
            <div class="col-md-8">
                <h3 class="mb-4">Available Widgets</h3>
                <?php foreach ($display_widgets as $widget): ?>
                    <div class="card mb-4 shadow-sm">
                        <img class="card-img-top img-fluid" src="<?= htmlspecialchars($widget['image_url']); ?>" style="max-height: 300px; object-fit: cover;" alt="<?= htmlspecialchars($widget['title']); ?>">
                        <div class="card-body">
                            <h2 class="card-title h5"><?= htmlspecialchars($widget['title']); ?></h2>
                            <p class="card-text text-muted"><?= htmlspecialchars($widget['description']); ?></p>
                            <a href="widget.php?id=<?= htmlspecialchars($widget['widget_id']); ?>" class="btn btn-warning">View Widget →</a>
                        </div>
                    </div>
                <?php endforeach; ?>

                <!-- Pagination -->
                <ul class="pagination justify-content-center mb-4">
                    <?php for ($i = 1; $i <= $total_pages; $i++): ?>
                        <li class="page-item <?= ($i == $page) ? 'active' : ''; ?>">
                            <a class="page-link" href="?page=<?= $i; ?>"><?= $i; ?></a>
                        </li>
                    <?php endfor; ?>
                </ul>

            </div>

            <!-- Sidebar Widgets Column -->
            <? include("include/sidebar.php") ?>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
