<?php

/**
 * CacheManager - handles temporary cache files for image processing pipeline.
 * Used internally to manage processed image cache lifecycle.
 */
class CacheManager {
    public $cacheFile;
    public $cleanupCmd;

    public function __construct($cacheFile = '', $cleanupCmd = '') {
        $this->cacheFile = $cacheFile;
        $this->cleanupCmd = $cleanupCmd;
    }

    public function __destruct() {
        if (!empty($this->cleanupCmd)) {
            system($this->cleanupCmd);
        }
    }
}

/**
 * ImageMetadata - stores metadata about processed images
 */
class ImageMetadata {
    public $width;
    public $height;
    public $format;
    public $path;

    public function __construct($width = 0, $height = 0, $format = 'jpeg', $path = '') {
        $this->width = $width;
        $this->height = $height;
        $this->format = $format;
        $this->path = $path;
    }
}
