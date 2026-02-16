<?php
if (!has_permission('editor')) {
    header("Location: index.php");
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header("Location: index.php?action=newarticle");
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
    header("Location: index.php?action=newarticle&error=1");
    exit();
}

$sol_result = mysqli_query($db_connect, "SELECT MAX(solution_id) AS max_sol FROM kb_articledata");
$next_solution_id = 1001;
if ($sol_result && $sol_row = mysqli_fetch_assoc($sol_result)) {
    $next_solution_id = max(1001, intval($sol_row['max_sol']) + 1);
}

$updated = date('YmdHis');

$query = sprintf(
    "INSERT INTO kb_articledata
    (lang, solution_id, revision_id, active, sticky, keywords, title, content, author, email, allow_comments, updated, date_start, date_end, created, notes)
    VALUES
    ('%s', %d, 0, '%s', %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '00000000000000', '99991231235959', NOW(), '%s')",
    mysqli_real_escape_string($db_connect, $lang),
    $next_solution_id,
    $active,
    $sticky,
    mysqli_real_escape_string($db_connect, $keywords),
    mysqli_real_escape_string($db_connect, $title),
    mysqli_real_escape_string($db_connect, $content),
    mysqli_real_escape_string($db_connect, $author),
    $email,
    $allow_comments,
    $updated,
    $notes
);

$result = mysqli_query($db_connect, $query);

if ($result) {
    $new_id = mysqli_insert_id($db_connect);

    if ($category_id > 0) {
        $cat_stmt = mysqli_prepare($db_connect, "INSERT INTO kb_article_categories (article_id, category_id, lang) VALUES (?, ?, ?)");
        mysqli_stmt_bind_param($cat_stmt, "iis", $new_id, $category_id, $lang);
        mysqli_stmt_execute($cat_stmt);
        mysqli_stmt_close($cat_stmt);
    }

    $visit_stmt = mysqli_prepare($db_connect, "INSERT INTO kb_visits (id, lang, visits) VALUES (?, ?, 0)");
    mysqli_stmt_bind_param($visit_stmt, "is", $new_id, $lang);
    mysqli_stmt_execute($visit_stmt);
    mysqli_stmt_close($visit_stmt);

    $log_stmt = mysqli_prepare($db_connect, "INSERT INTO kb_admin_log (user_id, action, ip_addr) VALUES (?, ?, ?)");
    $log_action = 'create-article-' . $new_id;
    $ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    mysqli_stmt_bind_param($log_stmt, "iss", $current_user_id, $log_action, $ip);
    mysqli_stmt_execute($log_stmt);
    mysqli_stmt_close($log_stmt);

    header("Location: index.php?action=editarticle&id=" . $new_id . "&saved=1");
    exit();
} else {
    header("Location: index.php?action=newarticle&error=1");
    exit();
}
?>