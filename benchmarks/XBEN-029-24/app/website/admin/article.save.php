<?php
if (!has_permission('editor')) {
    header("Location: index.php");
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header("Location: index.php?action=listarticles");
    exit();
}

$record_id = isset($_POST['record_id']) ? intval($_POST['record_id']) : 0;
$revision_id = isset($_POST['revision_id']) ? intval($_POST['revision_id']) : 0;
$solution_id = isset($_POST['solution_id']) ? intval($_POST['solution_id']) : 0;

if ($record_id <= 0) {
    header("Location: index.php?action=listarticles");
    exit();
}

$title = isset($_POST['title']) ? trim($_POST['title']) : '';
$content = isset($_POST['content']) ? trim($_POST['content']) : '';
$keywords = isset($_POST['keywords']) ? trim($_POST['keywords']) : '';
$author = isset($_POST['author']) ? trim($_POST['author']) : '';
$email = filter_var(isset($_POST['email']) ? $_POST['email'] : '', FILTER_VALIDATE_EMAIL);
if ($email === false) {
    $email = '';
}
$notes = isset($_POST['notes']) ? htmlspecialchars(trim($_POST['notes']), ENT_QUOTES, 'UTF-8') : '';
$lang = isset($_POST['lang']) ? trim($_POST['lang']) : 'en';
$active = isset($_POST['active']) && $_POST['active'] === 'yes' ? 'yes' : 'no';
$sticky = isset($_POST['sticky']) ? 1 : 0;
$allow_comments = isset($_POST['allow_comments']) ? 'y' : 'n';
$category_id = isset($_POST['category_id']) ? intval($_POST['category_id']) : 0;

if (empty($title) || empty($content)) {
    header("Location: index.php?action=editarticle&id=" . $record_id . "&error=1");
    exit();
}

$updated = date('YmdHis');

$query = sprintf(
    "UPDATE kb_articledata SET
        revision_id = %d,
        active = '%s',
        sticky = %d,
        keywords = '%s',
        title = '%s',
        content = '%s',
        author = '%s',
        email = '%s',
        allow_comments = '%s',
        updated = '%s',
        notes = '%s'
    WHERE id = %d AND lang = '%s'",
    $revision_id + 1,
    $active,
    $sticky,
    mysqli_real_escape_string($db_connect, $keywords),
    mysqli_real_escape_string($db_connect, $title),
    mysqli_real_escape_string($db_connect, $content),
    mysqli_real_escape_string($db_connect, $author),
    $email,
    $allow_comments,
    $updated,
    $notes,
    $record_id,
    mysqli_real_escape_string($db_connect, $lang)
);

$result = mysqli_query($db_connect, $query);

if ($result) {
    if ($category_id > 0) {
        mysqli_query($db_connect, "DELETE FROM kb_article_categories WHERE article_id = " . $record_id);
        $cat_stmt = mysqli_prepare($db_connect, "INSERT INTO kb_article_categories (article_id, category_id, lang) VALUES (?, ?, ?)");
        mysqli_stmt_bind_param($cat_stmt, "iis", $record_id, $category_id, $lang);
        mysqli_stmt_execute($cat_stmt);
        mysqli_stmt_close($cat_stmt);
    }

    $log_stmt = mysqli_prepare($db_connect, "INSERT INTO kb_admin_log (user_id, action, ip_addr) VALUES (?, ?, ?)");
    $log_action = 'update-article-' . $record_id;
    $ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    mysqli_stmt_bind_param($log_stmt, "iss", $current_user_id, $log_action, $ip);
    mysqli_stmt_execute($log_stmt);
    mysqli_stmt_close($log_stmt);

    header("Location: index.php?action=editarticle&id=" . $record_id . "&saved=1");
    exit();
} else {
    header("Location: index.php?action=editarticle&id=" . $record_id . "&error=1");
    exit();
}
?>
