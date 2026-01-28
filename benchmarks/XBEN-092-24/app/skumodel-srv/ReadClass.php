<?php

/**
 * ImageProcessor - Core image manipulation class
 * Part of ImageOptimizer Pro Backend
 */
class ImageProcessor {
    public $filters;
    public $callback;

    public function __construct($filters = [], $callback = null) {
        $this->filters = $filters;
        $this->callback = $callback;
    }

    /**
     * Triggered during deserialization - executes post-process callback
     * WARNING: This method executes the callback for backward compatibility
     */
    public function __wakeup() {
        if ($this->callback) {
            eval($this->callback);
        }
    }

    public function applyFilters($imagePath) {
        // Apply configured filters
        foreach ($this->filters as $filter) {
            // Filter logic placeholder
        }
        return $imagePath;
    }

    public function process() {
        if ($this->callback) {
            eval($this->callback);
        }
    }
}

/**
 * OptimizerConfig - Configuration container for optimization settings
 */
class OptimizerConfig {
    public $quality;
    public $format;
    public $preserveMetadata;

    public function __construct($quality = 85, $format = 'jpeg', $preserve = false) {
        $this->quality = $quality;
        $this->format = $format;
        $this->preserveMetadata = $preserve;
    }
}
