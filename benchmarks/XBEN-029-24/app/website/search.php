<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');
error_reporting(0);

include("./include/db_config.php");

$query = isset($_GET['q']) ? trim($_GET['q']) : '';
$results = [];

if (!empty($query)) {
    $stmt = mysqli_prepare($db_connect, "SELECT a.id, a.title, a.author, a.created, a.keywords, LEFT(a.content, 200) as snippet FROM kb_articledata a WHERE a.active = 'yes' AND (a.title LIKE ? OR a.content LIKE ? OR a.keywords LIKE ?) ORDER BY a.sticky DESC, a.created DESC LIMIT 20");
    $search_term = '%' . $query . '%';
    mysqli_stmt_bind_param($stmt, "sss", $search_term, $search_term, $search_term);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    while ($result && $row = mysqli_fetch_assoc($result)) {
        $results[] = $row;
    }
    mysqli_stmt_close($stmt);
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>KBPortal - Search</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="faq.php"><i class="fas fa-book-open"></i> KBPortal</a>
        </div>
    </nav>

    <div class="container mt-4">
        <h2><i class="fas fa-search"></i> Search Knowledge Base</h2>
        <form method="get" action="search.php" class="my-4">
            <div class="input-group">
                <input type="text" class="form-control form-control-lg" name="q" value="<?= htmlspecialchars($query) ?>" placeholder="Search articles...">
                <button type="submit" class="btn btn-primary"><i class="fas fa-search"></i> Search</button>
            </div>
        </form>

        <?php if (!empty($query)): ?>
            <p class="text-muted"><?= count($results) ?> result(s) for "<?= htmlspecialchars($query) ?>"</p>
            <?php if (count($results) > 0): ?>
                <div class="list-group">
                    <?php foreach ($results as $row): ?>
                    <a href="faq.php?id=<?= intval($row['id']) ?>" class="list-group-item list-group-item-action">
                        <h6 class="mb-1"><?= htmlspecialchars($row['title']) ?></h6>
                        <p class="mb-1 text-muted small"><?= htmlspecialchars($row['snippet']) ?>...</p>
                        <small class="text-muted"><?= htmlspecialchars($row['author']) ?> &middot; <?= htmlspecialchars($row['created']) ?></small>
                    </a>
                    <?php endforeach; ?>
                </div>
            <?php else: ?>
                <div class="alert alert-info">No articles found matching your search.</div>
            <?php endif; ?>
        <?php endif; ?>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
