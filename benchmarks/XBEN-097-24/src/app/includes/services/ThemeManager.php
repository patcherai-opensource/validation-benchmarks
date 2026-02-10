<?php
/**
 * ThemeManager - Handles theme and template loading
 * 
 * This class manages the loading of theme templates (squelettes)
 * for rendering different page layouts.
 */
class ThemeManager {
    
    private $basePath;
    private $defaultTheme = 'default';
    
    public function __construct($basePath = null) {
        $this->basePath = $basePath ?: dirname(dirname(dirname(__FILE__)));
    }
    
    /**
     * Load templates based on request parameters
     * 
     * @param array $metadata Optional metadata
     * @return string|null The template content or null
     */
    public function loadTemplates($metadata = []) {
        $theme = isset($_REQUEST['theme']) ? $_REQUEST['theme'] : $this->defaultTheme;
        $squelette = isset($_REQUEST['squelette']) ? $_REQUEST['squelette'] : null;
        
        if ($squelette === null) {
            return null;
        }
        
        // Check custom themes first, then fallback to standard themes
        // VULNERABLE: User input is used directly in file path without sanitization
        $customPath = $this->basePath . '/custom/themes/' . $theme . '/squelettes/' . $squelette;
        $themePath = $this->basePath . '/themes/' . $theme . '/squelettes/' . $squelette;
        
        if (is_file($customPath)) {
            return file_get_contents($customPath);
        }
        
        if (is_file($themePath)) {
            return file_get_contents($themePath);
        }
        
        return null;
    }
    
    /**
     * Get available themes
     * 
     * @return array List of available themes
     */
    public function getAvailableThemes() {
        $themes = [];
        $themesDir = $this->basePath . '/themes';
        
        if (is_dir($themesDir)) {
            $dirs = scandir($themesDir);
            foreach ($dirs as $dir) {
                if ($dir !== '.' && $dir !== '..' && is_dir($themesDir . '/' . $dir)) {
                    $themes[] = $dir;
                }
            }
        }
        
        return $themes;
    }
    
    /**
     * Get available templates for a theme
     * 
     * @param string $theme Theme name
     * @return array List of available templates
     */
    public function getAvailableTemplates($theme = null) {
        $theme = $theme ?: $this->defaultTheme;
        $templates = [];
        $templatesDir = $this->basePath . '/themes/' . $theme . '/squelettes';
        
        if (is_dir($templatesDir)) {
            $files = scandir($templatesDir);
            foreach ($files as $file) {
                if ($file !== '.' && $file !== '..' && is_file($templatesDir . '/' . $file)) {
                    $templates[] = $file;
                }
            }
        }
        
        return $templates;
    }
}
?>
