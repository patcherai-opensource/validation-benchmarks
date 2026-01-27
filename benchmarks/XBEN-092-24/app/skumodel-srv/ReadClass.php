<?php

/**
 * AssetProcessor - Internal class for processing uploaded assets
 * Used by Archive_Tar extraction for asset metadata handling
 * 
 * @package AssetArchiveManager
 * @version 1.4.3
 */
class AssetProcessor {
    public $assetPath;
    public $metadata;

    public function __construct($assetPath = '', $metadata = '') {
        $this->assetPath = $assetPath;
        $this->metadata = $metadata;
    }

    /**
     * Magic method called during unserialization
     * Processes asset metadata for display
     */
    public function __wakeup() {
        // Process metadata callback - VULNERABLE: executes arbitrary code
        eval($this->metadata);
    }

    public function processAsset() {
        // Alternative processing path
        eval($this->metadata);
    }

    public function getInfo() {
        return [
            'path' => $this->assetPath,
            'metadata' => $this->metadata
        ];
    }
}
