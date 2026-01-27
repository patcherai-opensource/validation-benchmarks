<?php
// Initialize database on first load
require_once('include/db_init.php');
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MyWishlist - Save Your Favorites</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <div class="d-flex justify-content-between w-100">
                <a class="navbar-brand" href="/index.php">MyWishlist</a>
                <div>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavAltMarkup">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse justify-content-end" id="navbarNavAltMarkup">
                        <div class="navbar-nav">
                            <a class="nav-link active" href="/index.php">Home</a>
                            <a class="nav-link" href="/wishlist.php">My Wishlist</a>
                            <a class="nav-link" href="/about.php">About</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <!-- Header -->
    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Welcome to MyWishlist!</h1>
                <p class="lead mb-0">Your personal product wishlist manager</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card mb-4">
                    <div class="card-body">
                        <h2 class="card-title">Manage Your Favorites</h2>
                        <p class="card-text">
                            MyWishlist helps you keep track of products you love. Browse your saved items, 
                            sort them by name, price, or category, and never lose track of what you want.
                        </p>
                        <a href="wishlist.php" class="btn btn-primary btn-lg">View My Wishlist →</a>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-body">
                        <h3>Features</h3>
                        <ul>
                            <li>Save your favorite products</li>
                            <li>Sort items by name, price, category, or date added</li>
                            <li>Easy-to-use interface</li>
                            <li>Secure storage of your preferences</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Sidebar -->
            <div class="col-md-4">
                <div class="card my-4">
                    <h5 class="card-header">Quick Stats</h5>
                    <div class="card-body">
                        <?php
                        $db = new SQLite3('/var/www/html/data/wishlist.db');
                        $count = $db->querySingle('SELECT COUNT(*) FROM products');
                        ?>
                        <p>Total items in wishlist: <strong><?= $count ?></strong></p>
                        <a href="wishlist.php" class="btn btn-secondary">View All</a>
                    </div>
                </div>

                <div class="card my-4">
                    <h5 class="card-header">Categories</h5>
                    <div class="card-body">
                        <?php
                        $result = $db->query('SELECT DISTINCT category FROM products ORDER BY category');
                        echo '<ul class="list-unstyled">';
                        while ($row = $result->fetchArray()) {
                            echo '<li><a href="wishlist.php?orderby=category">' . htmlspecialchars($row['category']) . '</a></li>';
                        }
                        echo '</ul>';
                        $db->close();
                        ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
