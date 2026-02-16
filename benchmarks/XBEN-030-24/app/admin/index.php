<?php
/**
 * Administration module router
 */

$page = gp_get_post('page', 'modules');

switch ($page) {
    case 'modules':
        require __DIR__ . '/modules.php';
        break;
    case 'customfields':
        require __DIR__ . '/customfields.php';
        break;
    case 'system':
        require __DIR__ . '/system.php';
        break;
    default:
        gp_redirect('/index.php?module=admin&page=modules');
        break;
}
