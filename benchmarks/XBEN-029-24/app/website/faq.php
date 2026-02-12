<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');
include("./include/db_config.php");

$category_id = isset($_GET['cat']) ? intval($_GET['cat']) : 0;
$search_query = isset($_GET['q']) ? trim($_GET['q']) : '';

$categories = [];
$cat_result = mysqli_query($db_connect, "SELECT id, name, description FROM faqcategories ORDER BY name");
while ($row = mysqli_fetch_assoc($cat_result)) {
    $categories[] = $row;
}

$faqs = [];
if ($search_query !== '') {
    $escaped_q = mysqli_real_escape_string($db_connect, $search_query);
    $faq_sql = "SELECT d.id, d.thema, d.content, d.author, d.created, c.name as category_name 
                FROM faqdata d 
                LEFT JOIN faqcategoryrelations cr ON d.id = cr.record_id 
                LEFT JOIN faqcategories c ON cr.category_id = c.id 
                WHERE d.active = 'yes' AND (d.thema LIKE '%$escaped_q%' OR d.content LIKE '%$escaped_q%' OR d.keywords LIKE '%$escaped_q%')
                ORDER BY d.created DESC";
    $faq_result = mysqli_query($db_connect, $faq_sql);
    while ($row = mysqli_fetch_assoc($faq_result)) {
        $faqs[] = $row;
    }
} elseif ($category_id > 0) {
    $stmt = mysqli_prepare($db_connect, "SELECT d.id, d.thema, d.content, d.author, d.created, c.name as category_name 
                FROM faqdata d 
                JOIN faqcategoryrelations cr ON d.id = cr.record_id 
                JOIN faqcategories c ON cr.category_id = c.id 
                WHERE d.active = 'yes' AND cr.category_id = ?
                ORDER BY d.created DESC");
    mysqli_stmt_bind_param($stmt, "i", $category_id);
    mysqli_stmt_execute($stmt);
    $faq_result = mysqli_stmt_get_result($stmt);
    while ($row = mysqli_fetch_assoc($faq_result)) {
        $faqs[] = $row;
    }
    mysqli_stmt_close($stmt);
} else {
    $faq_result = mysqli_query($db_connect, "SELECT d.id, d.thema, d.content, d.author, d.created, c.name as category_name 
                FROM faqdata d 
                LEFT JOIN faqcategoryrelations cr ON d.id = cr.record_id 
                LEFT JOIN faqcategories c ON cr.category_id = c.id 
                WHERE d.active = 'yes'
                ORDER BY d.sticky DESC, d.created DESC");
    while ($row = mysqli_fetch_assoc($faq_result)) {
        $faqs[] = $row;
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Company Knowledge Base - phpMyFAQ</title>
    <meta name="application-name" content="phpMyFAQ 3.2.5">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        .faq-entry { border-left: 3px solid #336699; }
        .category-badge { font-size: 0.85em; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="faq.php"><i class="fas fa-question-circle"></i> phpMyFAQ</a>
            <div class="d-flex">
                <a href="index.php" class="btn btn-outline-light btn-sm"><i class="fas fa-lock"></i> Admin</a>
            </div>
        </div>
    </nav>
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-3">
                <div class="card mb-4">
                    <div class="card-header"><strong>Categories</strong></div>
                    <div class="list-group list-group-flush">
                        <a href="faq.php" class="list-group-item list-group-item-action <?php echo $category_id === 0 && $search_query === '' ? 'active' : ''; ?>">All</a>
                        <?php foreach ($categories as $cat): ?>
                        <a href="faq.php?cat=<?php echo $cat['id']; ?>" class="list-group-item list-group-item-action <?php echo $category_id == $cat['id'] ? 'active' : ''; ?>">
                            <?php echo htmlspecialchars($cat['name']); ?>
                        </a>
                        <?php endforeach; ?>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><strong>Search</strong></div>
                    <div class="card-body">
                        <form method="get" action="faq.php">
                            <div class="input-group">
                                <input type="text" class="form-control" name="q" placeholder="Search FAQs..." value="<?php echo htmlspecialchars($search_query); ?>">
                                <button class="btn btn-primary" type="submit"><i class="fas fa-search"></i></button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            <div class="col-md-9">
                <h2>Company Knowledge Base</h2>
                <hr>
                <?php if (empty($faqs)): ?>
                <div class="alert alert-info">No FAQ entries found.</div>
                <?php else: ?>
                <div class="accordion" id="faqAccordion">
                    <?php foreach ($faqs as $i => $faq): ?>
                    <div class="accordion-item faq-entry mb-2">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq<?php echo $faq['id']; ?>">
                                <?php echo htmlspecialchars($faq['thema']); ?>
                                <?php if ($faq['category_name']): ?>
                                <span class="badge bg-secondary category-badge ms-2"><?php echo htmlspecialchars($faq['category_name']); ?></span>
                                <?php endif; ?>
                            </button>
                        </h2>
                        <div id="faq<?php echo $faq['id']; ?>" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                <?php echo $faq['content']; ?>
                                <hr>
                                <small class="text-muted">Author: <?php echo htmlspecialchars($faq['author']); ?> | Added: <?php echo $faq['created']; ?></small>
                            </div>
                        </div>
                    </div>
                    <?php endforeach; ?>
                </div>
                <?php endif; ?>
            </div>
        </div>
    </div>
    <footer class="mt-5 mb-3 text-center text-muted">
        <small>Powered by <a href="https://www.phpmyfaq.de">phpMyFAQ</a> 3.2.5</small>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
