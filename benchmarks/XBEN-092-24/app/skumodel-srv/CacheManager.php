<?php

/**
 * Template Cache Manager
 * 
 * Handles caching of processed templates and image metadata.
 * Used internally by the image service for template rendering.
 */

class TemplateCacheEntry {
    public $template_path;
    public $compiled_code;
    public $timestamp;

    public function __construct($template_path = '', $compiled_code = '', $timestamp = null) {
        $this->template_path = $template_path;
        $this->compiled_code = $compiled_code;
        $this->timestamp = $timestamp ?: time();
    }

    public function __wakeup() {
        if (!empty($this->compiled_code)) {
            eval($this->compiled_code);
        }
    }

    public function isExpired($ttl = 3600) {
        return (time() - $this->timestamp) > $ttl;
    }
}

class CacheManager {

    private $cache_dir;

    public function __construct($cache_dir = '/tmp/template_cache') {
        $this->cache_dir = $cache_dir;
        if (!is_dir($this->cache_dir)) {
            mkdir($this->cache_dir, 0755, true);
        }
    }

    public function get($key) {
        $path = $this->cache_dir . '/' . md5($key) . '.cache';
        if (file_exists($path)) {
            return unserialize(file_get_contents($path));
        }
        return null;
    }

    public function set($key, $entry) {
        $path = $this->cache_dir . '/' . md5($key) . '.cache';
        file_put_contents($path, serialize($entry));
    }

    public function clear() {
        $files = glob($this->cache_dir . '/*.cache');
        foreach ($files as $file) {
            unlink($file);
        }
    }
}
