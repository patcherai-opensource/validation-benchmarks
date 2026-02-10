<?php
/**
 * ThemeManager - Handles template loading and theme management
 */
class ThemeManager {
    private $themesDir;
    private $customThemesDir;
    private $defaultTheme = 'default';
    
    public function __construct() {
        $this->themesDir = dirname(dirname(__DIR__)) . '/themes';
        $this->customThemesDir = dirname(dirname(__DIR__)) . '/custom/themes';
    }
    
    /**
     * Load templates based on request parameters
     * @param array $metadata Additional metadata for template loading
     * @return array Template configuration
     */
    public function loadTemplates($metadata = []) {
        $templateConfig = [
            'theme' => $this->defaultTheme,
            'squelette' => 'main.php',
            'style' => 'default.css'
        ];
        
        // Get theme from request
        if (isset($_REQUEST['theme']) && !empty($_REQUEST['theme'])) {
            $templateConfig['theme'] = $_REQUEST['theme'];
        }
        
        // Get squelette (template) from request
        if (isset($_REQUEST['squelette']) && !empty($_REQUEST['squelette'])) {
            $squelette = $_REQUEST['squelette'];
            
            // Check custom themes directory first
            $customPath = $this->customThemesDir . '/' . $templateConfig['theme'] . '/squelettes/' . $squelette;
            if (is_file($customPath)) {
                $templateConfig['squelette'] = $squelette;
                $templateConfig['template_path'] = $customPath;
            } else {
                // Check standard themes directory
                $standardPath = $this->themesDir . '/' . $templateConfig['theme'] . '/squelettes/' . $squelette;
                if (is_file($standardPath)) {
                    $templateConfig['squelette'] = $squelette;
                    $templateConfig['template_path'] = $standardPath;
                }
            }
        }
        
        // If no custom template path set, use default
        if (!isset($templateConfig['template_path'])) {
            $templateConfig['template_path'] = $this->themesDir . '/' . $templateConfig['theme'] . '/squelettes/' . $templateConfig['squelette'];
        }
        
        // Get style from request
        if (isset($_REQUEST['style']) && !empty($_REQUEST['style'])) {
            $templateConfig['style'] = $_REQUEST['style'];
        }
        
        return $templateConfig;
    }
    
    /**
     * Render a template with given variables
     * @param string $templatePath Path to the template file
     * @param array $vars Variables to extract into template scope
     * @return string Rendered content
     */
    public function renderTemplate($templatePath, $vars = []) {
        if (!is_file($templatePath)) {
            return '<p>Template not found.</p>';
        }
        
        // Extract variables into current scope
        extract($vars);
        
        // Start output buffering
        ob_start();
        include($templatePath);
        $output = ob_get_clean();
        
        return $output;
    }
    
    /**
     * Get available themes
     * @return array List of available themes
     */
    public function getAvailableThemes() {
        $themes = [];
        
        if (is_dir($this->themesDir)) {
            $dirs = scandir($this->themesDir);
            foreach ($dirs as $dir) {
                if ($dir !== '.' && $dir !== '..' && is_dir($this->themesDir . '/' . $dir)) {
                    $themes[] = $dir;
                }
            }
        }
        
        return $themes;
    }
}
