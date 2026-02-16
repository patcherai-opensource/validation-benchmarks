<?php

require '../../includes/csrf.php';
require_once '../../includes/config.php';

$node = $_POST['node'];

if (isset($node)) {

    $pubkey = NETCFG_TUNNEL_PATH.$node.'-public.key';
    $privkey = NETCFG_TUNNEL_PATH.$node.'-private.key';
    $pubkey_tmp = '/tmp/'.$node.'-public.key';
    $privkey_tmp = '/tmp/'.$node.'-private.key';

    exec("sudo wg genkey | tee $privkey_tmp | wg pubkey > $pubkey_tmp", $return);
    $tunneldata['pubkey'] = str_replace("\n",'',@file_get_contents($pubkey_tmp));
    exec("sudo mv $privkey_tmp $privkey", $return);
    exec("sudo mv $pubkey_tmp $pubkey", $return);

    echo json_encode($tunneldata);
}
