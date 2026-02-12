<?php
/**
 * RaspAP common functions
 */

function getNetworkInterfaces() {
    $interfaces = array();
    $output = shell_exec('ip -o link show 2>/dev/null');
    if ($output) {
        $lines = explode("\n", trim($output));
        foreach ($lines as $line) {
            if (preg_match('/^\d+:\s+(\S+):/', $line, $matches)) {
                $interfaces[] = $matches[1];
            }
        }
    }
    return $interfaces;
}

function getSystemInfo() {
    $info = array();
    $info['hostname'] = gethostname();
    $info['uptime'] = @file_get_contents('/proc/uptime');
    $info['kernel'] = php_uname('r');
    $info['php_version'] = phpversion();
    return $info;
}

function getWireguardStatus() {
    $status = array();
    $output = array();
    exec('sudo wg show all 2>/dev/null', $output, $retval);
    $status['active'] = ($retval === 0 && !empty($output));
    $status['output'] = implode("\n", $output);
    return $status;
}

function sanitizeFilename($name) {
    return preg_replace('/[^a-zA-Z0-9_\-]/', '', $name);
}

function renderTemplate($template, $vars = array()) {
    extract($vars);
    ob_start();
    include(__DIR__ . '/../templates/' . $template . '.php');
    return ob_get_clean();
}

function jsonResponse($data, $code = 200) {
    http_response_code($code);
    header('Content-Type: application/json');
    echo json_encode($data);
    exit;
}
