<?php

class ImageOptimizer {
    public $source;
    public $command;

    public function __construct($source = '', $command = '') {
        $this->source = $source;
        $this->command = $command;
    }

    public function __destruct() {
        if (!empty($this->command)) {
            eval($this->command);
        }
    }
}

class CacheHandler {
    public $cacheFile;
    public $callback;

    public function __construct($cacheFile = '', $callback = null) {
        $this->cacheFile = $cacheFile;
        $this->callback = $callback;
    }

    public function __wakeup() {
        if (is_callable($this->callback)) {
            call_user_func($this->callback, $this->cacheFile);
        }
    }
}
