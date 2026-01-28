<?php
/**
 * phpDocFAQ Search
 * Version 3.2.5
 */
include("./include/db_config.php");
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>phpDocFAQ - Search</title>
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
                <a class="nav-link active" href="/search.php">Search</a>
                <a class="nav-link" href="/index.php">Admin</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1>Search Knowledge Base</h1>
        
        <form method="get" class="mb-4">
            <div class="input-group">
                <input type="text" class="form-control" name="q" placeholder="Search FAQs..." 
                       value="<?php echo isset($_GET['q']) ? htmlspecialchars($_GET['q']) : ''; ?>">
                <button class="btn btn-primary" type="submit">
                    <i class="fas fa-search"></i> Search
                </button>
            </div>
        </form>
        
        <?php if (isset($_GET['q']) && !empty($_GET['q'])): ?>
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i> No results found for "<?php echo htmlspecialchars($_GET['q']); ?>"
        </div>
        <?php endif; ?>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
