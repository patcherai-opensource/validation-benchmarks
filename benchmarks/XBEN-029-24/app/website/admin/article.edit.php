<?php
if (!has_permission('editor')) {
    echo '<div class="alert alert-danger">You do not have permission to access this page.</div>';
    return;
}

$article_id = isset($_GET['id']) ? intval($_GET['id']) : 0;
$is_edit = ($action === 'editarticle' && $article_id > 0);

$article = [
    'id' => 0,
    'lang' => 'en',
    'solution_id' => 0,
    'revision_id' => 0,
    'active' => 'no',
    'sticky' => 0,
    'keywords' => '',
    'title' => '',
    'content' => '',
    'author' => $current_display_name,
    'email' => '',
    'allow_comments' => 'y',
    'notes' => '',
];

$selected_category = 0;

if ($is_edit) {
    $page_title = 'Edit Article';
    $stmt = mysqli_prepare($db_connect, "SELECT * FROM kb_articledata WHERE id = ?");
    mysqli_stmt_bind_param($stmt, "i", $article_id);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    if ($result && $row = mysqli_fetch_assoc($result)) {
        $article = $row;
    } else {
        echo '<div class="alert alert-danger">Article not found.</div>';
        include(__DIR__ . "/layout_footer.php");
        return;
    }
    mysqli_stmt_close($stmt);

    $cat_r = mysqli_query($db_connect, "SELECT category_id FROM kb_article_categories WHERE article_id = " . intval($article_id) . " LIMIT 1");
    if ($cat_r && $cat_row = mysqli_fetch_assoc($cat_r)) {
        $selected_category = intval($cat_row['category_id']);
    }
} else {
    $page_title = 'Add New Article';
}

$categories = [];
$cat_result = mysqli_query($db_connect, "SELECT category_id, name FROM kb_categories ORDER BY display_order");
while ($cat_result && $cat_row = mysqli_fetch_assoc($cat_result)) {
    $categories[] = $cat_row;
}

include(__DIR__ . "/layout_header.php");

$form_action = $is_edit ? 'savearticle' : 'addarticle';
?>

<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">
        <i class="fas fa-<?= $is_edit ? 'edit' : 'plus-circle' ?>"></i>
        <?= $is_edit ? 'Edit Article #' . intval($article['id']) : 'Add New Article' ?>
    </h1>
</div>

<?php if (isset($_GET['saved'])): ?>
    <div class="alert alert-success alert-dismissible fade show">
        <i class="fas fa-check-circle"></i> Article saved successfully.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
<?php endif; ?>

<?php if (isset($_GET['error'])): ?>
    <div class="alert alert-danger alert-dismissible fade show">
        <i class="fas fa-exclamation-triangle"></i> Failed to save article. Please check your input and try again.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
<?php endif; ?>

<form method="post" action="index.php?action=<?= $form_action ?>">
    <?php if ($is_edit): ?>
        <input type="hidden" name="record_id" value="<?= intval($article['id']) ?>">
        <input type="hidden" name="revision_id" value="<?= intval($article['revision_id']) ?>">
        <input type="hidden" name="solution_id" value="<?= intval($article['solution_id']) ?>">
    <?php endif; ?>

    <div class="row">
        <div class="col-md-9">
            <div class="card shadow-sm mb-3">
                <div class="card-header"><h6 class="mb-0">Article Content</h6></div>
                <div class="card-body">
                    <div class="mb-3">
                        <label for="title" class="form-label">Title <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="title" name="title" required
                               value="<?= htmlspecialchars($article['title']) ?>">
                    </div>
                    <div class="mb-3">
                        <label for="content" class="form-label">Content <span class="text-danger">*</span></label>
                        <textarea class="form-control" id="content" name="content" rows="12" required><?= htmlspecialchars($article['content']) ?></textarea>
                    </div>
                    <div class="mb-3">
                        <label for="keywords" class="form-label">Keywords</label>
                        <input type="text" class="form-control" id="keywords" name="keywords"
                               value="<?= htmlspecialchars($article['keywords'] ?? '') ?>"
                               placeholder="Comma-separated keywords">
                    </div>
                </div>
            </div>

            <div class="card shadow-sm mb-3">
                <div class="card-header"><h6 class="mb-0">Author Information</h6></div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="author" class="form-label">Author Name <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="author" name="author" required
                                   value="<?= htmlspecialchars($article['author']) ?>">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="email" class="form-label">Author Email <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="email" name="email" required
                                   value="<?= htmlspecialchars($article['email']) ?>"
                                   placeholder="author@example.com">
                            <div class="form-text">Contact email for this article's author.</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card shadow-sm mb-3">
                <div class="card-header"><h6 class="mb-0">Internal Notes</h6></div>
                <div class="card-body">
                    <div class="mb-0">
                        <label for="notes" class="form-label">Admin Notes</label>
                        <textarea class="form-control" id="notes" name="notes" rows="3"
                                  placeholder="Internal notes visible only to editors..."><?= htmlspecialchars($article['notes'] ?? '') ?></textarea>
                        <div class="form-text">These notes are not shown publicly and are for internal use only.</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card shadow-sm mb-3">
                <div class="card-header"><h6 class="mb-0">Publishing</h6></div>
                <div class="card-body">
                    <div class="mb-3">
                        <label for="active" class="form-label">Status</label>
                        <select class="form-select" id="active" name="active">
                            <option value="yes" <?= ($article['active'] === 'yes') ? 'selected' : '' ?>>Published</option>
                            <option value="no" <?= ($article['active'] !== 'yes') ? 'selected' : '' ?>>Draft</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="sticky" name="sticky" value="1"
                                   <?= ($article['sticky']) ? 'checked' : '' ?>>
                            <label class="form-check-label" for="sticky">Sticky article</label>
                        </div>
                    </div>
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="allow_comments" name="allow_comments" value="y"
                                   <?= ($article['allow_comments'] === 'y') ? 'checked' : '' ?>>
                            <label class="form-check-label" for="allow_comments">Allow comments</label>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card shadow-sm mb-3">
                <div class="card-header"><h6 class="mb-0">Category</h6></div>
                <div class="card-body">
                    <select class="form-select" name="category_id">
                        <option value="0">-- Select Category --</option>
                        <?php foreach ($categories as $cat): ?>
                            <option value="<?= intval($cat['category_id']) ?>"
                                    <?= ($selected_category == $cat['category_id']) ? 'selected' : '' ?>>
                                <?= htmlspecialchars($cat['name']) ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>
            </div>

            <div class="card shadow-sm mb-3">
                <div class="card-header"><h6 class="mb-0">Language</h6></div>
                <div class="card-body">
                    <select class="form-select" name="lang">
                        <option value="en" <?= ($article['lang'] === 'en') ? 'selected' : '' ?>>English</option>
                        <option value="de" <?= ($article['lang'] === 'de') ? 'selected' : '' ?>>German</option>
                        <option value="fr" <?= ($article['lang'] === 'fr') ? 'selected' : '' ?>>French</option>
                        <option value="es" <?= ($article['lang'] === 'es') ? 'selected' : '' ?>>Spanish</option>
                    </select>
                </div>
            </div>

            <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary btn-lg">
                    <i class="fas fa-save"></i> <?= $is_edit ? 'Save Changes' : 'Create Article' ?>
                </button>
                <a href="index.php?action=listarticles" class="btn btn-outline-secondary">
                    <i class="fas fa-times"></i> Cancel
                </a>
            </div>
        </div>
    </div>
</form>

<?php include(__DIR__ . "/layout_footer.php"); ?>
