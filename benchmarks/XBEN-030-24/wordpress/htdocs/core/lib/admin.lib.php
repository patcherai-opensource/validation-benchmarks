<?php
/**
 * Dolibarr ERP & CRM - Admin helper functions
 *
 * @package  Dolibarr\Core
 */

/**
 * Print the main page header
 *
 * @param  string  $title  Page title
 * @param  object  $user   User object
 * @return void
 */
function llxHeader($title = '', $user = null)
{
    header('Content-Type: text/html; charset=UTF-8');
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: SAMEORIGIN');
    ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo dol_escape_htmltag($title); ?> - Dolibarr ERP/CRM</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #f4f5f7; color: #333; font-size: 13px; }
        a { color: #3367a6; text-decoration: none; }
        a:hover { text-decoration: underline; }

        /* Top menu bar */
        .tmenu { background: #263c5c; padding: 0 20px; display: flex; align-items: center; min-height: 48px; }
        .tmenu .logo { color: #fff; font-size: 16px; font-weight: 600; margin-right: 30px; }
        .tmenu .logo span { font-weight: 300; font-size: 11px; opacity: 0.6; }
        .tmenu nav { display: flex; gap: 0; flex: 1; }
        .tmenu nav a { color: #b8c7d9; padding: 14px 16px; font-size: 13px; display: inline-block; }
        .tmenu nav a:hover, .tmenu nav a.active { color: #fff; background: rgba(255,255,255,0.1); text-decoration: none; }
        .tmenu .user-info { color: #b8c7d9; font-size: 12px; margin-left: auto; }
        .tmenu .user-info a { color: #b8c7d9; }

        /* Left sidebar */
        .side-container { display: flex; min-height: calc(100vh - 48px); }
        .sidebar { width: 220px; background: #fff; border-right: 1px solid #d8dce3; padding: 10px 0; flex-shrink: 0; }
        .sidebar .sidebar-title { padding: 8px 16px; font-size: 12px; color: #999; text-transform: uppercase; font-weight: 600; }
        .sidebar a { display: block; padding: 7px 16px 7px 24px; color: #555; font-size: 13px; }
        .sidebar a:hover, .sidebar a.active { background: #eef1f6; color: #333; text-decoration: none; }

        /* Main content */
        .main-content { flex: 1; padding: 20px 30px; max-width: 1200px; }
        .fiche { background: #fff; border: 1px solid #d8dce3; border-radius: 3px; padding: 20px; margin-bottom: 15px; }
        h2.titre { font-size: 16px; font-weight: 500; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 1px solid #eee; }

        /* Tables */
        table.liste { width: 100%; border-collapse: collapse; }
        table.liste th { background: #f5f7fa; padding: 8px 10px; text-align: left; border-bottom: 2px solid #d8dce3; font-weight: 600; font-size: 12px; color: #555; }
        table.liste td { padding: 8px 10px; border-bottom: 1px solid #eee; }
        table.liste tr:hover td { background: #f9fafb; }
        table.border { width: 100%; border-collapse: collapse; }
        table.border td { padding: 6px 10px; border: 1px solid #ddd; vertical-align: top; }
        table.border .titlefield { background: #f5f7fa; font-weight: 500; width: 25%; color: #555; }

        /* Form elements */
        .flat { padding: 6px 10px; border: 1px solid #ccc; border-radius: 3px; font-size: 13px; font-family: inherit; }
        .flat:focus { border-color: #4a90d9; outline: none; }
        select.flat { background: #fff; }
        textarea.flat { width: 100%; min-height: 60px; }
        input.flat[type="text"], input.flat[type="password"] { width: 250px; }

        /* Buttons */
        .button { padding: 7px 18px; background: #263c5c; color: #fff; border: none; border-radius: 3px; font-size: 13px; cursor: pointer; font-family: inherit; }
        .button:hover { background: #1a2d47; }
        .butAction { display: inline-block; padding: 7px 18px; background: #263c5c; color: #fff !important; border-radius: 3px; margin: 4px 2px; }
        .butAction:hover { background: #1a2d47; text-decoration: none; }
        .butActionDelete { display: inline-block; padding: 7px 18px; background: #bc3434; color: #fff !important; border-radius: 3px; margin: 4px 2px; }
        .butActionDelete:hover { background: #992828; text-decoration: none; }

        /* Messages */
        .jnotify-container { margin-bottom: 10px; }
        .jnotify-notification { padding: 10px 14px; border-radius: 3px; margin-bottom: 5px; }
        .jnotify-notification-info { background: #dff0d8; border: 1px solid #c3e6a8; color: #3c763d; }
        .jnotify-notification-error { background: #f2dede; border: 1px solid #ebccd1; color: #a94442; }

        /* Badges */
        .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
        .badge-status1 { background: #dff0d8; color: #3c763d; }
        .badge-status5 { background: #fcf8e3; color: #8a6d3b; }
        .badge-status0 { background: #f2dede; color: #a94442; }

        /* Tab headers */
        .tabs { display: flex; border-bottom: 2px solid #263c5c; margin-bottom: 15px; }
        .tabs a { padding: 8px 16px; color: #555; font-size: 13px; display: inline-block; border: 1px solid transparent; border-bottom: none; margin-bottom: -2px; }
        .tabs a:hover { color: #333; text-decoration: none; }
        .tabs a.active { background: #fff; border-color: #d8dce3; border-bottom: 2px solid #fff; color: #263c5c; font-weight: 500; }

        .breadcrumb { font-size: 12px; color: #999; margin-bottom: 12px; }
        .breadcrumb a { color: #3367a6; }
    </style>
</head>
<body>
<div class="tmenu">
    <div class="logo">Dolibarr <span>19.0.1</span></div>
    <nav>
        <a href="/admin/index.php">Home</a>
        <a href="/user/index.php" class="<?php echo (strpos($_SERVER['REQUEST_URI'], '/user/') !== false) ? 'active' : ''; ?>">Users & Groups</a>
        <a href="/admin/modules.php">Setup</a>
    </nav>
    <?php if ($user && $user->id) { ?>
    <div class="user-info">
        <?php echo dol_escape_htmltag($user->getFullName()); ?>
        <?php if ($user->admin) { echo ' <span style="color:#f0c040;">(admin)</span>'; } ?>
        &nbsp;|&nbsp; <a href="/index.php?action=logout">Logout</a>
    </div>
    <?php } ?>
</div>
<?php
}

/**
 * Print the page footer
 *
 * @return void
 */
function llxFooter()
{
    ?>
</body>
</html>
<?php
}

/**
 * Print the left sidebar for user admin area
 *
 * @return void
 */
function printUserAdminSidebar()
{
    ?>
<div class="sidebar">
    <div class="sidebar-title">Users & Groups</div>
    <a href="/user/index.php">Users list</a>
    <a href="/user/admin/user_extrafields.php" class="<?php echo (basename($_SERVER['SCRIPT_NAME']) == 'user_extrafields.php') ? 'active' : ''; ?>">Extra fields</a>
    <div class="sidebar-title" style="margin-top: 10px;">Setup</div>
    <a href="/admin/modules.php">Modules</a>
    <a href="/admin/index.php">System information</a>
</div>
<?php
}
