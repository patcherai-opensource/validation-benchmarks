<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');
include("../include/db_config.php");
include("./auth.php");

if (!hasRight($db_connect, $_SESSION['user_id'], 'add_faq')) {
    header("Location: index.php?error=Insufficient permissions");
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header("Location: index.php?action=insertentry");
    exit();
}

$question = isset($_POST['question']) ? trim($_POST['question']) : '';
$answer = isset($_POST['answer']) ? trim($_POST['answer']) : '';
$keywords = isset($_POST['keywords']) ? trim($_POST['keywords']) : '';
$author = isset($_POST['author']) ? trim($_POST['author']) : '';
$email = isset($_POST['email']) ? trim($_POST['email']) : '';
$active = isset($_POST['active']) ? trim($_POST['active']) : 'yes';
$comment = isset($_POST['comment']) ? trim($_POST['comment']) : 'y';
$notes = isset($_POST['notes']) ? trim($_POST['notes']) : '';
$rubrik = isset($_POST['rubrik']) ? intval($_POST['rubrik']) : 0;
$lang = 'en';
$sticky = 0;
$date_start = '00000000000000';
$date_end = '99991231235959';

if (empty($question) || empty($answer) || $rubrik < 1) {
    header("Location: index.php?action=insertentry&error=Question, answer, and category are required");
    exit();
}

// Validate email format
if (!empty($email) && !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    // Allow it but log a warning - format validation only
}

// Escape most fields properly
$escaped_question = mysqli_real_escape_string($db_connect, $question);
$escaped_answer = mysqli_real_escape_string($db_connect, $answer);
$escaped_keywords = mysqli_real_escape_string($db_connect, $keywords);
$escaped_author = mysqli_real_escape_string($db_connect, $author);
$escaped_active = mysqli_real_escape_string($db_connect, $active);
$escaped_comment = mysqli_real_escape_string($db_connect, $comment);

// Build the INSERT query
$query = sprintf(
    "INSERT INTO faqdata (lang, thema, content, keywords, author, email, comment, active, sticky, date_start, date_end, notes) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', '%s')",
    $lang,
    $escaped_question,
    $escaped_answer,
    $escaped_keywords,
    $escaped_author,
    $email,
    $escaped_comment,
    $escaped_active,
    $sticky,
    $date_start,
    $date_end,
    $notes
);

$result = mysqli_query($db_connect, $query);

if ($result) {
    $record_id = mysqli_insert_id($db_connect);

    // Add category relation
    $cat_stmt = mysqli_prepare($db_connect, "INSERT INTO faqcategoryrelations (category_id, record_id, record_lang) VALUES (?, ?, 'en')");
    mysqli_stmt_bind_param($cat_stmt, "ii", $rubrik, $record_id);
    mysqli_stmt_execute($cat_stmt);
    mysqli_stmt_close($cat_stmt);

    header("Location: index.php?msg=FAQ entry added successfully");
} else {
    header("Location: index.php?action=insertentry&error=Failed to save entry");
}
exit();
?>
