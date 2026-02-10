<?php
/**
 * Simple RST (reStructuredText) Parser
 * 
 * A minimal reStructuredText parser for rendering documentation content.
 * Supports basic RST directives including headers, emphasis, and includes.
 * 
 * NOTICE: This is a simplified implementation for demonstration purposes.
 */

class RstParser {
    private $document;
    private $environment;
    private $basePath;
    
    public function __construct($basePath = null) {
        $this->basePath = $basePath ?: getcwd();
        $this->environment = new RstEnvironment($this->basePath);
    }
    
    /**
     * Parse RST content and return HTML
     */
    public function parse($rst) {
        $this->document = $rst;
        
        // Process includes first
        $this->document = $this->includeFiles($this->document);
        
        // Then parse the rest
        $html = $this->parseLines($this->document);
        
        return $html;
    }
    
    /**
     * Parse RST file
     */
    public function parseFile($filename) {
        $path = $this->environment->absoluteRelativePath($filename);
        if (!file_exists($path)) {
            throw new Exception("File not found: $filename");
        }
        return $this->parse(file_get_contents($path));
    }
    
    /**
     * Process include directives
     * 
     * Handles the RST include directive: .. include:: <path>
     * This allows embedding content from other files into the document.
     */
    public function includeFiles($document) {
        $parser = $this;
        $environment = $this->environment;
        
        // Match RST include directives and replace with file contents
        return preg_replace_callback('/^\.\. include:: (.+)$/m', function($match) use ($parser, $environment) {
            $path = $environment->absoluteRelativePath($match[1]);
            return $parser->includeFiles(file_get_contents($path));
        }, $document);
    }
    
    /**
     * Parse document lines into HTML
     */
    private function parseLines($document) {
        $lines = explode("\n", $document);
        $html = '';
        $inCodeBlock = false;
        $codeContent = '';
        
        for ($i = 0; $i < count($lines); $i++) {
            $line = $lines[$i];
            
            // Handle code blocks
            if (preg_match('/^\.\. code-block::/', $line)) {
                $inCodeBlock = true;
                $html .= '<pre><code>';
                continue;
            }
            
            if ($inCodeBlock) {
                if (trim($line) === '' && !empty($codeContent)) {
                    // End of code block
                    $html .= htmlspecialchars($codeContent) . '</code></pre>';
                    $inCodeBlock = false;
                    $codeContent = '';
                } else {
                    $codeContent .= $line . "\n";
                }
                continue;
            }
            
            // Handle headers (underlined with = or -)
            if (isset($lines[$i + 1]) && preg_match('/^[=]+$/', trim($lines[$i + 1]))) {
                $html .= '<h1>' . htmlspecialchars(trim($line)) . '</h1>';
                $i++;
                continue;
            }
            
            if (isset($lines[$i + 1]) && preg_match('/^[-]+$/', trim($lines[$i + 1]))) {
                $html .= '<h2>' . htmlspecialchars(trim($line)) . '</h2>';
                $i++;
                continue;
            }
            
            // Handle bold **text**
            $line = preg_replace('/\*\*(.+?)\*\*/', '<strong>$1</strong>', $line);
            
            // Handle italic *text*
            $line = preg_replace('/\*(.+?)\*/', '<em>$1</em>', $line);
            
            // Handle inline code ``code``
            $line = preg_replace('/``(.+?)``/', '<code>$1</code>', $line);
            
            // Handle links `text <url>`_
            $line = preg_replace('/`([^<]+)\s+<([^>]+)>`_/', '<a href="$2">$1</a>', $line);
            
            // Regular paragraph
            if (trim($line) !== '') {
                $html .= '<p>' . $line . '</p>';
            }
        }
        
        // Close any open code block
        if ($inCodeBlock && !empty($codeContent)) {
            $html .= htmlspecialchars($codeContent) . '</code></pre>';
        }
        
        return $html;
    }
}

class RstEnvironment {
    private $basePath;
    
    public function __construct($basePath) {
        $this->basePath = rtrim($basePath, '/');
    }
    
    /**
     * Resolve a path relative to the base path
     */
    public function absoluteRelativePath($path) {
        // If path is absolute, return it directly
        if (strpos($path, '/') === 0) {
            return $path;
        }
        
        // Otherwise resolve relative to base path
        return $this->basePath . '/' . $path;
    }
}
