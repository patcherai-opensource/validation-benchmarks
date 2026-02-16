<?php
/**
 * Page layout and template functions
 */

function gp_page_header($title = '', $extra_head = '') {
    $user = get_current_user_info();
    $app_name = APP_NAME;
    $version = APP_VERSION;
    ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo gp_escape_html($title ? $title . ' - ' . $app_name : $app_name); ?></title>
    <link rel="stylesheet" href="/public/css/style.css">
    <?php echo $extra_head; ?>
</head>
<body>
<div id="gp-wrapper">
    <div id="gp-topmenu">
        <div class="gp-topmenu-left">
            <a href="/index.php" class="gp-logo"><?php echo gp_escape_html($app_name); ?></a>
            <span class="gp-version">v<?php echo gp_escape_html($version); ?></span>
        </div>
        <?php if (!empty($user['id'])): ?>
        <div class="gp-topmenu-nav">
            <a href="/index.php?module=employee&action=list">Employees</a>
            <a href="/index.php?module=project&action=list">Projects</a>
            <?php if ($user['admin']): ?>
            <a href="/index.php?module=admin&page=modules">Administration</a>
            <?php endif; ?>
        </div>
        <div class="gp-topmenu-right">
            <span class="gp-user"><?php echo gp_escape_html($user['name']); ?></span>
            <a href="/index.php?module=logout" class="gp-logout">Logout</a>
        </div>
        <?php endif; ?>
    </div>
    <div id="gp-main">
    <?php
}

function gp_page_footer() {
    ?>
    </div>
    <div id="gp-footer">
        <p><?php echo APP_NAME; ?> &copy; <?php echo date('Y'); ?> - Version <?php echo APP_VERSION; ?></p>
    </div>
</div>
</body>
</html>
    <?php
}

function gp_page_title($title, $linkback = '') {
    echo '<div class="gp-page-title">';
    if ($linkback) {
        echo '<a href="' . gp_escape_html($linkback) . '" class="gp-back">&laquo; Back</a>';
    }
    echo '<h2>' . gp_escape_html($title) . '</h2>';
    echo '</div>';
}

function gp_show_message($msg, $type = 'info') {
    echo '<div class="gp-msg gp-msg-' . gp_escape_html($type) . '">' . gp_escape_html($msg) . '</div>';
}

function gp_admin_tabs($active = '') {
    $tabs = array(
        'modules' => array('label' => 'Modules', 'url' => '/index.php?module=admin&page=modules'),
        'customfields' => array('label' => 'Custom Fields', 'url' => '/index.php?module=admin&page=customfields&entitytype=employee'),
        'system' => array('label' => 'System Info', 'url' => '/index.php?module=admin&page=system'),
    );

    echo '<div class="gp-tabs">';
    foreach ($tabs as $key => $tab) {
        $cls = ($key === $active) ? ' class="active"' : '';
        echo '<a href="' . gp_escape_html($tab['url']) . '"' . $cls . '>' . gp_escape_html($tab['label']) . '</a>';
    }
    echo '</div>';
}
