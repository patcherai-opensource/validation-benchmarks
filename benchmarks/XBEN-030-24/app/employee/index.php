<?php
/**
 * Employee module router
 */

require_once APP_ROOT . '/core/class/employee.class.php';
require_once APP_ROOT . '/core/class/customfields.class.php';

$action = gp_get_post('action', 'list');

switch ($action) {
    case 'view':
        require __DIR__ . '/card.php';
        break;
    case 'list':
    default:
        require __DIR__ . '/list.php';
        break;
}
