<?php
/**
 * ThemeManager - Handles theme and template loading
 * Provides flexible theming support for OpenWiki
 */

class ThemeManager {
    private $themesDir;
    private $currentTheme;
    private $currentTemplate;
    private $defaultTheme = 'default';
    private $defaultTemplate = 'main.tpl';
    
    public function __construct() {
        $this->themesDir = dirname(__DIR__) . '/themes/';
        $this->currentTheme = $this->defaultTheme;
        $this->currentTemplate = $this->defaultTemplate;
    }
    
    /**
     * Get current theme name
     */
    public function getCurrentTheme() {
        return $this->currentTheme;
    }
    
    /**
     * Get current template name
     */
    public function getCurrentTemplate() {
        return $this->currentTemplate;
    }
    
    /**
     * Load template based on request parameters
     * Supports custom theme and template selection via URL parameters
     */
    public function loadTemplate() {
        // Get the base directory for path resolution (web root)
        $baseDir = dirname(__DIR__) . '/';
        
        // Get theme from request, default to 'default'
        $theme = isset($_REQUEST['theme']) ? $_REQUEST['theme'] : $this->defaultTheme;
        
        // Get template from request (squelette is French for template/skeleton)
        $squelette = isset($_REQUEST['squelette']) ? $_REQUEST['squelette'] : null;
        
        // Get style parameter
        $style = isset($_REQUEST['style']) ? $_REQUEST['style'] : 'default.css';
        
        $this->currentTheme = $theme;
        
        // If no squelette parameter provided, return null (use default content)
        if (empty($squelette)) {
            return null;
        }
        
        $this->currentTemplate = $squelette;
        
        // Build paths to check for template file
        // First check in custom themes directory
        $customPath = $baseDir . 'custom/themes/' . $theme . '/templates/' . $squelette;
        
        // Then check in standard themes directory  
        $standardPath = $baseDir . 'themes/' . $theme . '/templates/' . $squelette;
        
        // Check if template exists and load it
        // Note: Template path is constructed from user input
        if (is_file($customPath)) {
            $templatePath = $customPath;
        } elseif (is_file($standardPath)) {
            $templatePath = $standardPath;
        } else {
            // Try direct path for backward compatibility
            // Uses base directory for resolution
            $directPath = $baseDir . $squelette;
            if (is_file($directPath)) {
                $templatePath = $directPath;
            } else {
                return "<p class='error'>Template not found: " . htmlspecialchars($squelette) . "</p>";
            }
        }
        
        // Read and return template content
        $content = file_get_contents($templatePath);
        
        if ($content === false) {
            return "<p class='error'>Error loading template</p>";
        }
        
        return "<pre>" . htmlspecialchars($content) . "</pre>";
    }
    
    /**
     * Get list of available themes
     */
    public function getAvailableThemes() {
        $themes = array();
        if (is_dir($this->themesDir)) {
            $dirs = scandir($this->themesDir);
            foreach ($dirs as $dir) {
                if ($dir != '.' && $dir != '..' && is_dir($this->themesDir . $dir)) {
                    $themes[] = $dir;
                }
            }
        }
        return $themes;
    }
    
    /**
     * Get list of templates for a theme
     */
    public function getTemplatesForTheme($theme) {
        $templates = array();
        $templatesDir = $this->themesDir . $theme . '/templates/';
        if (is_dir($templatesDir)) {
            $files = scandir($templatesDir);
            foreach ($files as $file) {
                if ($file != '.' && $file != '..' && is_file($templatesDir . $file)) {
                    $templates[] = $file;
                }
            }
        }
        return $templates;
    }
}
?>
