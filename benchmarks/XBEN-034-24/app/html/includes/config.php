<?php
define('APP_NAME', 'PluginForge');
define('APP_VERSION', '3.9.0');
define('PLUGINS_DIR', __DIR__ . '/../plugins');
define('UPLOAD_DIR', '/tmp/plugin-uploads');
define('MAX_UPLOAD_SIZE', 50 * 1024 * 1024);

if (!is_dir(PLUGINS_DIR)) {
    mkdir(PLUGINS_DIR, 0755, true);
}
if (!is_dir(UPLOAD_DIR)) {
    mkdir(UPLOAD_DIR, 0755, true);
}

function get_installed_plugins() {
    $plugins = [];
    $pluginDir = PLUGINS_DIR;
    
    if (!is_dir($pluginDir)) {
        return $plugins;
    }
    
    $dirs = scandir($pluginDir);
    foreach ($dirs as $dir) {
        if ($dir === '.' || $dir === '..') continue;
        $manifestPath = $pluginDir . '/' . $dir . '/plugin.properties';
        if (file_exists($manifestPath)) {
            $props = parse_ini_file($manifestPath);
            $plugins[] = [
                'id' => $dir,
                'name' => $props['plugin.id'] ?? $dir,
                'version' => $props['plugin.version'] ?? 'unknown',
                'description' => $props['plugin.description'] ?? '',
                'provider' => $props['plugin.provider'] ?? 'Unknown',
                'class' => $props['plugin.class'] ?? '',
                'requires' => $props['plugin.requires'] ?? '*',
                'license' => $props['plugin.license'] ?? 'Apache-2.0',
                'status' => 'STARTED',
                'installed_at' => date('Y-m-d H:i:s', filemtime($manifestPath)),
            ];
        }
    }
    return $plugins;
}

function get_system_info() {
    return [
        'runtime_version' => APP_VERSION,
        'php_version' => phpversion(),
        'os' => php_uname('s') . ' ' . php_uname('r'),
        'plugins_directory' => PLUGINS_DIR,
        'upload_max' => ini_get('upload_max_filesize'),
    ];
}
