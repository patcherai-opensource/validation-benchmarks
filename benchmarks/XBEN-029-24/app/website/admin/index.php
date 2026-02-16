<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');
error_reporting(0);

include(__DIR__ . "/../include/db_config.php");
include(__DIR__ . "/auth_check.php");

$action = isset($_GET['action']) ? $_GET['action'] : 'dashboard';

$page_title = 'Dashboard';
$page_content = '';

switch ($action) {
    case 'dashboard':
        include(__DIR__ . "/dashboard.php");
        break;
    case 'listarticles':
        $page_title = 'All Articles';
        include(__DIR__ . "/article.list.php");
        break;
    case 'newarticle':
        $page_title = 'Add New Article';
        include(__DIR__ . "/article.edit.php");
        break;
    case 'editarticle':
        $page_title = 'Edit Article';
        include(__DIR__ . "/article.edit.php");
        break;
    case 'savearticle':
        include(__DIR__ . "/article.save.php");
        break;
    case 'addarticle':
        include(__DIR__ . "/article.add.php");
        break;
    case 'categories':
        $page_title = 'Categories';
        include(__DIR__ . "/category.list.php");
        break;
    default:
        include(__DIR__ . "/dashboard.php");
        break;
}
?>
