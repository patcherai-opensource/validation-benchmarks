<?php

require '../../includes/csrf.php';
require_once '../../includes/config.php';

$cfgFile = NETCFG_TUNNEL_CONFIG;
if (file_exists($cfgFile)) {
    echo file_get_contents($cfgFile);
} else {
    echo json_encode(['error' => 'No tunnel configuration found']);
}
