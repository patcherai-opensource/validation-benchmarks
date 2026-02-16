<?php
require_once __DIR__ . '/PackageExtractor.php';

/**
 * PackageManager - Manages extension package lifecycle including
 * upload, installation, listing, and removal.
 */
class PackageManager {

    private $packagesDir;
    private $installDir;

    public function __construct($packagesDir, $installDir) {
        $this->packagesDir = $packagesDir;
        $this->installDir = $installDir;

        if (!is_dir($this->packagesDir)) {
            mkdir($this->packagesDir, 0755, true);
        }
        if (!is_dir($this->installDir)) {
            mkdir($this->installDir, 0755, true);
        }
    }

    /**
     * Validate that the archive contains a proper extension descriptor.
     */
    public function validatePackage($filePath) {
        $zip = new ZipArchive();
        if ($zip->open($filePath) !== true) {
            return array('valid' => false, 'message' => 'Not a valid ZIP archive');
        }

        $hasDescriptor = false;
        for ($i = 0; $i < $zip->numFiles; $i++) {
            $name = $zip->getNameIndex($i);
            if (preg_match('/extension\.properties$|MANIFEST\.MF$/', $name)) {
                $hasDescriptor = true;
                break;
            }
        }
        $zip->close();

        if (!$hasDescriptor) {
            return array(
                'valid' => false,
                'message' => 'Missing package descriptor (extension.properties or MANIFEST.MF)'
            );
        }

        return array('valid' => true, 'message' => 'Valid package');
    }

    /**
     * If the given file is a ZIP, expand it into the install directory.
     */
    public function expandIfArchive($filePath) {
        if (!is_file($filePath) || !preg_match('/\.zip$/i', $filePath)) {
            return $filePath;
        }

        $basename = pathinfo($filePath, PATHINFO_FILENAME);
        $targetDir = $this->installDir . DIRECTORY_SEPARATOR . $basename;

        $fileMtime = filemtime($filePath);
        if (is_dir($targetDir)) {
            $dirMtime = filemtime($targetDir);
            if ($fileMtime <= $dirMtime) {
                return $targetDir;
            }
        }

        $extractor = new PackageExtractor();
        $extractor->setSource($filePath);
        $extractor->setTarget($targetDir);
        $extractor->extract();

        return $targetDir;
    }

    /**
     * Get list of installed extension metadata.
     */
    public function getInstalledExtensions() {
        $extensions = array();
        if (!is_dir($this->installDir)) {
            return $extensions;
        }

        $entries = scandir($this->installDir);
        foreach ($entries as $entry) {
            if ($entry === '.' || $entry === '..') continue;
            $extPath = $this->installDir . DIRECTORY_SEPARATOR . $entry;
            if (!is_dir($extPath)) continue;

            $meta = array(
                'id' => $entry,
                'name' => $entry,
                'version' => 'unknown',
                'provider' => 'unknown',
                'description' => '',
                'status' => 'active'
            );

            $propsFile = $extPath . DIRECTORY_SEPARATOR . 'extension.properties';
            if (is_file($propsFile)) {
                $props = $this->readProperties($propsFile);
                if (isset($props['extension.id'])) $meta['id'] = $props['extension.id'];
                if (isset($props['extension.name'])) $meta['name'] = $props['extension.name'];
                if (isset($props['extension.version'])) $meta['version'] = $props['extension.version'];
                if (isset($props['extension.provider'])) $meta['provider'] = $props['extension.provider'];
                if (isset($props['extension.description'])) $meta['description'] = $props['extension.description'];
            }

            $extensions[] = $meta;
        }

        return $extensions;
    }

    /**
     * Get uploaded packages list.
     */
    public function getUploadedPackages() {
        $packages = array();
        if (!is_dir($this->packagesDir)) {
            return $packages;
        }

        $entries = scandir($this->packagesDir);
        foreach ($entries as $entry) {
            if ($entry === '.' || $entry === '..') continue;
            $fpath = $this->packagesDir . DIRECTORY_SEPARATOR . $entry;
            if (is_file($fpath)) {
                $packages[] = array(
                    'name' => $entry,
                    'size' => filesize($fpath)
                );
            }
        }

        return $packages;
    }

    /**
     * Remove a package and its extracted contents.
     */
    public function removePackage($packageId) {
        $safeName = basename($packageId);
        $pkgPath = $this->packagesDir . DIRECTORY_SEPARATOR . $safeName;
        if (is_file($pkgPath)) {
            unlink($pkgPath);
        }

        $extName = pathinfo($safeName, PATHINFO_FILENAME);
        $extPath = $this->installDir . DIRECTORY_SEPARATOR . $extName;
        if (is_dir($extPath)) {
            $this->removeDirectory($extPath);
        }

        return array('status' => 'removed', 'package' => $safeName);
    }

    private function readProperties($path) {
        $props = array();
        if (!is_file($path)) return $props;

        $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        foreach ($lines as $line) {
            $line = trim($line);
            if (empty($line) || $line[0] === '#') continue;
            $pos = strpos($line, '=');
            if ($pos !== false) {
                $key = trim(substr($line, 0, $pos));
                $val = trim(substr($line, $pos + 1));
                $props[$key] = $val;
            }
        }
        return $props;
    }

    private function removeDirectory($dir) {
        $items = scandir($dir);
        foreach ($items as $item) {
            if ($item === '.' || $item === '..') continue;
            $path = $dir . DIRECTORY_SEPARATOR . $item;
            if (is_dir($path)) {
                $this->removeDirectory($path);
            } else {
                unlink($path);
            }
        }
        rmdir($dir);
    }
}
