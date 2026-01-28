<?php
/**
 * phpDocFAQ Public FAQ Viewer
 * Version 3.2.5
 */
include("./include/db_config.php");
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>phpDocFAQ - Knowledge Base</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="generator" content="phpDocFAQ 3.2.5">
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
        <h1>Frequently Asked Questions</h1>
        <p class="lead">Browse our knowledge base by category</p>
        
        <div class="row">
            <?php
            $categories_query = "SELECT * FROM categories ORDER BY category_id";
            $categories_result = mysqli_query($db_connect, $categories_query);
            while ($cat = mysqli_fetch_assoc($categories_result)):
            ?>
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="fas fa-folder text-primary"></i> 
                            <?php echo htmlspecialchars($cat['name']); ?>
                        </h5>
                        <p class="card-text text-muted">
                            <?php echo htmlspecialchars($cat['description']); ?>
                        </p>
                        <a href="/category.php?id=<?php echo $cat['category_id']; ?>" class="btn btn-outline-primary btn-sm">
                            View FAQs
                        </a>
                    </div>
                </div>
            </div>
            <?php endwhile; ?>
        </div>
    </div>

    <footer class="bg-light mt-5 py-3">
        <div class="container text-center">
            <small class="text-muted">Powered by phpDocFAQ 3.2.5</small>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
