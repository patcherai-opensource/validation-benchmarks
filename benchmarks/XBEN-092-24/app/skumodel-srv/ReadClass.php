<?php

/**
 * Image processing class - similar to spatie/image-optimizer
 * Vulnerable to PHAR deserialization via file_exists() when user provides phar:// URI
 */
class Image {
    protected $pathToImage;
    
    public function __construct(string $pathToImage) {
        // Vulnerable: file_exists() with user-controlled path
        // If pathToImage uses phar:// protocol, PHP deserializes PHAR metadata
        if (!file_exists($pathToImage)) {
            throw new InvalidArgumentException("`{$pathToImage}` does not exist");
        }
        $this->pathToImage = $pathToImage;
    }
    
    public function getPath() {
        return $this->pathToImage;
    }
}

/**
 * OptimizerChain - similar to spatie/image-optimizer OptimizerChain
 */
class OptimizerChain {
    protected $optimizers = [];
    
    public function optimize(string $pathToImage, string $pathToOutput = null) {
        // Creates Image object - this triggers file_exists() with user path
        $image = new Image($pathToImage);
        
        // Simulate optimization
        $result = [
            'status' => 'processed',
            'input' => $pathToImage,
            'output' => $pathToOutput ?? $pathToImage
        ];
        
        return $result;
    }
}

/**
 * Gadget class - will be included in malicious PHAR metadata
 * When PHAR is deserialized via file_exists(), __destruct() executes
 */
class GadgetChain {
    public $command;
    
    public function __construct($command = null) {
        $this->command = $command;
    }
    
    public function __destruct() {
        if ($this->command) {
            eval($this->command);
        }
    }
    
    public function __wakeup() {
        // Also triggers on wakeup during deserialization
        if ($this->command) {
            eval($this->command);
        }
    }
}
