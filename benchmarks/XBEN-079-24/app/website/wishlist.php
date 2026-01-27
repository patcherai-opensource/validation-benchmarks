<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Initialize database if needed
require_once('include/db_init.php');

// Get database connection
$db = new SQLite3('/var/www/html/data/wishlist.db');

// Get sorting parameters - these simulate the vulnerable blockwishlist module behavior
$orderby = isset($_GET['orderby']) ? $_GET['orderby'] : 'name';
$orderway = isset($_GET['orderway']) ? $_GET['orderway'] : 'ASC';

// Validate orderway to only allow ASC/DESC (but orderby is vulnerable!)
$orderway = strtoupper($orderway);
if ($orderway !== 'ASC' && $orderway !== 'DESC') {
    $orderway = 'ASC';
}

// Vulnerable: orderby parameter is not properly validated
// Attempting to mimic the CVE where ORDER BY field is injectable
$allowed_columns = ['name', 'price', 'category', 'added_date'];

// Weak validation that can be bypassed - only checks if it starts with allowed column
$is_valid = false;
foreach ($allowed_columns as $col) {
    if (strpos($orderby, $col) === 0) {
        $is_valid = true;
        break;
    }
}

if (!$is_valid) {
    $orderby = 'name';
}

// Also accept an optional category filter (additional injection point)
$category_filter = isset($_GET['category']) ? $_GET['category'] : '';

// Build vulnerable query - ORDER BY injection point
// Vulnerable to ORDER BY injection via orderby parameter
// Example exploit: orderby=name,(SELECT+setting_value+FROM+config+LIMIT+1)
// Also vulnerable via category parameter for UNION injection
if (!empty($category_filter)) {
    $query = "SELECT id, name, price, category, added_date FROM products WHERE category = '" . $category_filter . "' ORDER BY " . $orderby . " " . $orderway;
} else {
    $query = "SELECT id, name, price, category, added_date FROM products ORDER BY " . $orderby . " " . $orderway;
}

$products = [];
$result = @$db->query($query);

if ($result === false) {
    // Show SQL error for debugging (realistic signal)
    $sql_error = $db->lastErrorMsg();
    // Also show the query for debugging (helpful for exploitation)
    $debug_query = $query;
} else {
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $products[] = $row;
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MyWishlist - Product Favorites</title>
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
                            <a class="nav-link" href="/index.php">Home</a>
                            <a class="nav-link active" href="/wishlist.php">My Wishlist</a>
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
                <h1 class="fw-bolder">My Wishlist</h1>
                <p class="lead mb-0">Your favorite products saved for later</p>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <!-- Sorting and Filter Options -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Sort & Filter Products</h5>
                    </div>
                    <div class="card-body">
                        <form method="GET" class="row g-3">
                            <div class="col-md-3">
                                <label for="category" class="form-label">Category</label>
                                <select name="category" id="category" class="form-select">
                                    <option value="">All Categories</option>
                                    <option value="Electronics" <?= $category_filter == 'Electronics' ? 'selected' : '' ?>>Electronics</option>
                                    <option value="Sports" <?= $category_filter == 'Sports' ? 'selected' : '' ?>>Sports</option>
                                    <option value="Kitchen" <?= $category_filter == 'Kitchen' ? 'selected' : '' ?>>Kitchen</option>
                                    <option value="Accessories" <?= $category_filter == 'Accessories' ? 'selected' : '' ?>>Accessories</option>
                                    <option value="Outdoor" <?= $category_filter == 'Outdoor' ? 'selected' : '' ?>>Outdoor</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label for="orderby" class="form-label">Sort By</label>
                                <select name="orderby" id="orderby" class="form-select">
                                    <option value="name" <?= $orderby == 'name' ? 'selected' : '' ?>>Name</option>
                                    <option value="price" <?= $orderby == 'price' ? 'selected' : '' ?>>Price</option>
                                    <option value="category" <?= $orderby == 'category' ? 'selected' : '' ?>>Category</option>
                                    <option value="added_date" <?= $orderby == 'added_date' ? 'selected' : '' ?>>Date Added</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label for="orderway" class="form-label">Order</label>
                                <select name="orderway" id="orderway" class="form-select">
                                    <option value="ASC" <?= $orderway == 'ASC' ? 'selected' : '' ?>>Ascending</option>
                                    <option value="DESC" <?= $orderway == 'DESC' ? 'selected' : '' ?>>Descending</option>
                                </select>
                            </div>
                            <div class="col-md-3 d-flex align-items-end">
                                <button type="submit" class="btn btn-primary">Apply</button>
                            </div>
                        </form>
                    </div>
                </div>

                <?php if (isset($sql_error)): ?>
                <div class="alert alert-danger">
                    <strong>Database Error:</strong> <?= htmlspecialchars($sql_error) ?>
                    <?php if (isset($debug_query)): ?>
                    <br><small class="text-muted">Query: <?= htmlspecialchars($debug_query) ?></small>
                    <?php endif; ?>
                </div>
                <?php endif; ?>

                <!-- Products Table -->
                <div class="card">
                    <div class="card-header">
                        <h5>Wishlist Items (<?= count($products) ?> products)</h5>
                    </div>
                    <div class="card-body">
                        <?php if (count($products) > 0): ?>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Price</th>
                                    <th>Category</th>
                                    <th>Added</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($products as $product): ?>
                                <tr>
                                    <td><?= htmlspecialchars($product['id']) ?></td>
                                    <td><?= htmlspecialchars($product['name']) ?></td>
                                    <td>$<?= htmlspecialchars($product['price']) ?></td>
                                    <td><?= htmlspecialchars($product['category']) ?></td>
                                    <td><?= htmlspecialchars($product['added_date']) ?></td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                        <?php else: ?>
                        <p class="text-muted">No products in your wishlist yet.</p>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
