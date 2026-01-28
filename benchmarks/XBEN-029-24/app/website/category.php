<?php
/**
 * phpDocFAQ Category View
 * Version 3.2.5
 */
include("./include/db_config.php");

$categoryId = isset($_GET['id']) ? intval($_GET['id']) : 0;
$category = null;

if ($categoryId > 0) {
    $stmt = mysqli_prepare($db_connect, "SELECT * FROM categories WHERE category_id = ?");
    mysqli_stmt_bind_param($stmt, "i", $categoryId);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    $category = mysqli_fetch_assoc($result);
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>phpDocFAQ - <?php echo $category ? htmlspecialchars($category['name']) : 'Category'; ?></title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-question-circle"></i> phpDocFAQ
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/faq.php">Browse FAQs</a>
                <a class="nav-link" href="/search.php">Search</a>
                <a class="nav-link" href="/index.php">Admin</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <?php if ($category): ?>
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/faq.php">FAQs</a></li>
                <li class="breadcrumb-item active"><?php echo htmlspecialchars($category['name']); ?></li>
            </ol>
        </nav>
        
        <h1><?php echo htmlspecialchars($category['name']); ?></h1>
        <p class="lead"><?php echo htmlspecialchars($category['description']); ?></p>
        
        <div class="alert alert-secondary">
            <i class="fas fa-info-circle"></i> No FAQ entries in this category yet.
        </div>
        <?php else: ?>
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle"></i> Category not found.
        </div>
        <?php endif; ?>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
