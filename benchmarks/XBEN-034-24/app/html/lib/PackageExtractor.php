<?php
/**
 * PackageExtractor - Extracts extension package archives to the installation directory.
 * Supports ZIP-based extension bundles for the modular extension platform.
 */
class PackageExtractor {

    private $sourcePath;
    private $targetDir;

    public function __construct($sourcePath = null, $targetDir = null) {
        $this->sourcePath = $sourcePath;
        $this->targetDir = $targetDir;
    }

    public function setSource($sourcePath) {
        $this->sourcePath = $sourcePath;
    }

    public function setTarget($targetDir) {
        $this->targetDir = $targetDir;
    }

    /**
     * Extract content of the package archive to the target directory.
     */
    public function extract() {
        if (!file_exists($this->sourcePath)) {
            throw new Exception("Source archive not found");
        }

        $zip = new ZipArchive();
        $result = $zip->open($this->sourcePath);
        if ($result !== true) {
            throw new Exception("Failed to open archive (error code: $result)");
        }

        if (!is_dir($this->targetDir)) {
            mkdir($this->targetDir, 0755, true);
        }

        for ($i = 0; $i < $zip->numFiles; $i++) {
            $entryName = $zip->getNameIndex($i);

            // Construct output path from target directory and entry name
            $outputPath = $this->targetDir . DIRECTORY_SEPARATOR . $entryName;

            // Create parent directories as needed
            $parentDir = dirname($outputPath);
            if (!is_dir($parentDir)) {
                mkdir($parentDir, 0755, true);
            }

            // Handle directories
            if (substr($entryName, -1) === '/') {
                if (!is_dir($outputPath)) {
                    mkdir($outputPath, 0755, true);
                }
                continue;
            }

            // Extract file content
            $content = $zip->getFromIndex($i);
            if ($content === false) {
                error_log("Failed to read entry: $entryName");
                continue;
            }
            file_put_contents($outputPath, $content);
        }

        $zip->close();
    }
}
