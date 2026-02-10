<?php
if (!defined('ABSPATH')) {
    define('ABSPATH', dirname(dirname(dirname(dirname(dirname(dirname(__FILE__)))))) . '/');
}

require_once(ABSPATH . 'wp-admin/admin.php');

$request_subdomain = sanitize_text_field($_REQUEST['subdomain'] ?? '');
$request_app_api = sanitize_text_field($_REQUEST['app_api'] ?? '');
$request_id = sanitize_text_field($_REQUEST['id'] ?? '');
$request_quality = sanitize_text_field($_REQUEST['quality'] ?? '');
$request_token = sanitize_text_field($_REQUEST['token'] ?? '');

if (isset($request_subdomain) && isset($request_app_api) && isset($request_id) && $request_subdomain && $request_app_api && $request_id) {
    $quality = $request_quality ?: 'preview';
    $url = 'https://' . $request_subdomain . '.' . $request_app_api . '/api_binary/v1/advance/image/' . $request_id . '/download/directuri?type=jpg&dpi=72';

    $args_for_get = array(
        'Authorization' => 'Bearer ' . $request_token,
    );
    
    $response = wp_remote_get($url,
        array(
            'method' => 'GET',
            'headers' => $args_for_get,
            'timeout' => 120,
        )
    );

    $body = wp_remote_retrieve_body($response);

    echo wp_json_encode($body);
}
