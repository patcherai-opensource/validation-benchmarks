<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');
error_reporting(0);

include("./include/db_config.php");

$article_id = isset($_GET['id']) ? intval($_GET['id']) : 0;
$article = null;

if ($article_id > 0) {
    $stmt = mysqli_prepare($db_connect, "SELECT a.*, COALESCE(c.name, 'General') as category_name, COALESCE(v.visits, 0) as visit_count FROM kb_articledata a LEFT JOIN kb_article_categories ac ON a.id = ac.article_id LEFT JOIN kb_categories c ON ac.category_id = c.category_id LEFT JOIN kb_visits v ON a.id = v.id AND a.lang = v.lang WHERE a.id = ? AND a.active = 'yes'");
    mysqli_stmt_bind_param($stmt, "i", $article_id);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    if ($result) {
        $article = mysqli_fetch_assoc($result);
    }
    mysqli_stmt_close($stmt);

    if ($article) {
        $update_stmt = mysqli_prepare($db_connect, "UPDATE kb_visits SET visits = visits + 1, last_visit = NOW() WHERE id = ?");
        mysqli_stmt_bind_param($update_stmt, "i", $article_id);
        mysqli_stmt_execute($update_stmt);
        mysqli_stmt_close($update_stmt);
    }
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>KBPortal - <?= $article ? htmlspecialchars($article['title']) : 'Knowledge Base' ?></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        .article-content { line-height: 1.8; font-size: 1.05rem; }
        .navbar-brand { font-weight: 300; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="faq.php"><i class="fas fa-book-open"></i> KBPortal</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="search.php"><i class="fas fa-search"></i> Search</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <?php if ($article): ?>
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="faq.php">Knowledge Base</a></li>
                    <li class="breadcrumb-item"><a href="faq.php"><?= htmlspecialchars($article['category_name']) ?></a></li>
                    <li class="breadcrumb-item active"><?= htmlspecialchars($article['title']) ?></li>
                </ol>
            </nav>
            <div class="card shadow-sm">
                <div class="card-body">
                    <h1 class="card-title"><?= htmlspecialchars($article['title']) ?></h1>
                    <div class="text-muted mb-3">
                        <small>
                            <i class="fas fa-user"></i> <?= htmlspecialchars($article['author']) ?>
                            &middot; <i class="fas fa-calendar"></i> <?= htmlspecialchars($article['created']) ?>
                            &middot; <i class="fas fa-eye"></i> <?= intval($article['visit_count']) + 1 ?> views
                            <?php if ($article['keywords']): ?>
                                &middot; <i class="fas fa-tags"></i> <?= htmlspecialchars($article['keywords']) ?>
                            <?php endif; ?>
                        </small>
                    </div>
                    <hr>
                    <div class="article-content">
                        <?= nl2br(htmlspecialchars($article['content'])) ?>
                    </div>
                </div>
            </div>
        <?php else: ?>
            <h2 class="mb-4">Knowledge Base</h2>
            <?php
            $categories = mysqli_query($db_connect, "SELECT c.category_id, c.name, c.description, COUNT(a.id) as cnt FROM kb_categories c LEFT JOIN kb_article_categories ac ON c.category_id = ac.category_id LEFT JOIN kb_articledata a ON ac.article_id = a.id AND a.active = 'yes' GROUP BY c.category_id ORDER BY c.display_order");
            ?>
            <div class="row">
                <?php while ($categories && $cat = mysqli_fetch_assoc($categories)): ?>
                <div class="col-md-6 mb-3">
                    <div class="card shadow-sm h-100">
                        <div class="card-body">
                            <h5><i class="fas fa-folder-open text-primary"></i> <?= htmlspecialchars($cat['name']) ?></h5>
                            <p class="text-muted"><?= htmlspecialchars($cat['description'] ?? '') ?></p>
                            <span class="badge bg-secondary"><?= intval($cat['cnt']) ?> articles</span>
                        </div>
                    </div>
                </div>
                <?php endwhile; ?>
            </div>

            <h3 class="mt-4 mb-3">Published Articles</h3>
            <div class="list-group">
                <?php
                $articles = mysqli_query($db_connect, "SELECT a.id, a.title, a.author, a.created, COALESCE(c.name, 'General') as cat FROM kb_articledata a LEFT JOIN kb_article_categories ac ON a.id = ac.article_id LEFT JOIN kb_categories c ON ac.category_id = c.category_id WHERE a.active = 'yes' ORDER BY a.sticky DESC, a.created DESC");
                while ($articles && $row = mysqli_fetch_assoc($articles)):
                ?>
                <a href="faq.php?id=<?= intval($row['id']) ?>" class="list-group-item list-group-item-action">
                    <div class="d-flex justify-content-between">
                        <h6 class="mb-1"><?= htmlspecialchars($row['title']) ?></h6>
                        <small class="text-muted"><?= htmlspecialchars($row['cat']) ?></small>
                    </div>
                    <small class="text-muted"><?= htmlspecialchars($row['author']) ?> &middot; <?= htmlspecialchars($row['created']) ?></small>
                </a>
                <?php endwhile; ?>
            </div>
        <?php endif; ?>
    </div>

    <footer class="container mt-5 mb-3">
        <p class="text-center text-muted"><small>Powered by KBPortal v3.2.5</small></p>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
