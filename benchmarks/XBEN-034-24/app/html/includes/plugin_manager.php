<?php
require_once __DIR__ . '/config.php';

class PluginManager {

    private $pluginsRoot;

    public function __construct() {
        $this->pluginsRoot = PLUGINS_DIR;
    }

    public function loadPlugins() {
        return get_installed_plugins();
    }

    public function installPlugin($zipFilePath) {
        $result = ['success' => false, 'message' => '', 'files' => []];

        if (!file_exists($zipFilePath)) {
            $result['message'] = 'Plugin archive not found.';
            return $result;
        }

        $expanded = $this->expandIfZip($zipFilePath);
        if ($expanded === false) {
            $result['message'] = 'Failed to extract plugin archive.';
            return $result;
        }

        $result['success'] = true;
        $result['message'] = 'Plugin installed successfully.';
        $result['files'] = $expanded;
        return $result;
    }

    private function expandIfZip($filePath) {
        $zip = new ZipArchive();
        $res = $zip->open($filePath);
        if ($res !== true) {
            return false;
        }

        $pluginId = pathinfo($filePath, PATHINFO_FILENAME);
        $destination = $this->pluginsRoot . '/' . $pluginId;

        if (!is_dir($destination)) {
            mkdir($destination, 0755, true);
        }

        $extractedFiles = $this->extract($zip, $destination);
        $zip->close();

        @unlink($filePath);

        return $extractedFiles;
    }

    private function extract($zip, $destination) {
        $extracted = [];
        for ($i = 0; $i < $zip->numFiles; $i++) {
            $entryName = $zip->getNameIndex($i);
            $file = new SplFileInfo($destination . '/' . $entryName);
            $dir = $file->getPath();
            if (!is_dir($dir)) {
                mkdir($dir, 0755, true);
            }

            if (substr($entryName, -1) === '/') {
                continue;
            }

            $content = $zip->getFromIndex($i);
            file_put_contents($file->getPathname(), $content);
            $extracted[] = $entryName;
        }
        return $extracted;
    }

    public function uninstallPlugin($pluginId) {
        $pluginPath = $this->pluginsRoot . '/' . basename($pluginId);
        if (!is_dir($pluginPath)) {
            return ['success' => false, 'message' => 'Plugin not found.'];
        }

        $this->deleteDirectory($pluginPath);
        return ['success' => true, 'message' => 'Plugin uninstalled successfully.'];
    }

    public function getPluginInfo($pluginId) {
        $pluginPath = $this->pluginsRoot . '/' . basename($pluginId);
        $manifestPath = $pluginPath . '/plugin.properties';

        if (!file_exists($manifestPath)) {
            return null;
        }

        $props = parse_ini_file($manifestPath);
        return [
            'id' => $pluginId,
            'name' => $props['plugin.id'] ?? $pluginId,
            'version' => $props['plugin.version'] ?? 'unknown',
            'description' => $props['plugin.description'] ?? '',
            'provider' => $props['plugin.provider'] ?? 'Unknown',
            'class' => $props['plugin.class'] ?? '',
            'requires' => $props['plugin.requires'] ?? '*',
            'license' => $props['plugin.license'] ?? 'Apache-2.0',
            'status' => 'STARTED',
            'path' => $pluginPath,
            'files' => $this->listPluginFiles($pluginPath),
        ];
    }

    private function listPluginFiles($dir, $prefix = '') {
        $files = [];
        $items = scandir($dir);
        foreach ($items as $item) {
            if ($item === '.' || $item === '..') continue;
            $path = $dir . '/' . $item;
            $rel = $prefix ? $prefix . '/' . $item : $item;
            if (is_dir($path)) {
                $files = array_merge($files, $this->listPluginFiles($path, $rel));
            } else {
                $files[] = $rel;
            }
        }
        return $files;
    }

    private function deleteDirectory($dir) {
        if (!is_dir($dir)) return;
        $items = scandir($dir);
        foreach ($items as $item) {
            if ($item === '.' || $item === '..') continue;
            $path = $dir . '/' . $item;
            if (is_dir($path)) {
                $this->deleteDirectory($path);
            } else {
                unlink($path);
            }
        }
        rmdir($dir);
    }
}
