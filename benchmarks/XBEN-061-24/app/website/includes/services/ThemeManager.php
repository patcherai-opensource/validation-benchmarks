<?php
/**
 * ThemeManager - Handles template loading and theme resolution
 * 
 * Manages the mapping between page requests and their visual templates,
 * supporting custom theme overrides and per-page template selection.
 */
class ThemeManager
{
    private $defaultTheme = 'margot';
    private $defaultStyle = 'margot.css';
    private $defaultSquelette = 'default.html';
    
    private $theme;
    private $style;
    private $squelette;
    private $templateContent = null;
    
    public function __construct()
    {
        $this->theme = $this->defaultTheme;
        $this->style = $this->defaultStyle;
        $this->squelette = $this->defaultSquelette;
    }
    
    /**
     * Load templates based on page metadata and request parameters.
     * Request parameters override page-level settings.
     */
    public function loadTemplates($metadata = [])
    {
        // Page-level metadata can set defaults
        if (!empty($metadata['theme'])) {
            $this->theme = $metadata['theme'];
        }
        if (!empty($metadata['style'])) {
            $this->style = $metadata['style'];
        }
        if (!empty($metadata['squelette'])) {
            $this->squelette = $metadata['squelette'];
        }
        
        // Request parameters override page metadata
        if (!empty($_REQUEST['theme'])) {
            $this->theme = $_REQUEST['theme'];
        }
        if (!empty($_REQUEST['style'])) {
            $this->style = $_REQUEST['style'];
        }
        if (!empty($_REQUEST['squelette'])) {
            $this->squelette = $_REQUEST['squelette'];
        }
        
        // Try to locate the template file
        // First check custom themes directory, then standard themes
        $templateFile = null;
        
        if (is_file('custom/themes/' . $this->theme . '/squelettes/' . $this->squelette)) {
            $templateFile = 'custom/themes/' . $this->theme . '/squelettes/' . $this->squelette;
        } elseif (is_file('themes/' . $this->theme . '/squelettes/' . $this->squelette)) {
            $templateFile = 'themes/' . $this->theme . '/squelettes/' . $this->squelette;
        }
        
        if ($templateFile !== null) {
            $this->templateContent = file_get_contents($templateFile);
        } else {
            // Fall back to default template
            $defaultPath = 'themes/' . $this->defaultTheme . '/squelettes/' . $this->defaultSquelette;
            if (is_file($defaultPath)) {
                $this->templateContent = file_get_contents($defaultPath);
            }
        }
    }
    
    /**
     * Render the loaded template with given page content
     */
    public function render($pageContent, $pageTitle = '', $pageMetadata = [])
    {
        if ($this->templateContent === null) {
            return $pageContent;
        }
        
        $output = $this->templateContent;
        
        // Replace template placeholders
        $output = str_replace('{{PAGE_CONTENT}}', $pageContent, $output);
        $output = str_replace('{{PAGE_TITLE}}', htmlspecialchars($pageTitle), $output);
        $output = str_replace('{{THEME}}', htmlspecialchars($this->theme), $output);
        $output = str_replace('{{STYLE}}', htmlspecialchars($this->style), $output);
        
        // Process any remaining metadata placeholders
        foreach ($pageMetadata as $key => $value) {
            $output = str_replace('{{' . strtoupper($key) . '}}', htmlspecialchars($value), $output);
        }
        
        return $output;
    }
    
    public function getTheme()
    {
        return $this->theme;
    }
    
    public function getStyle()
    {
        return $this->style;
    }
    
    public function getSquelette()
    {
        return $this->squelette;
    }
    
    public function getStylePath()
    {
        $customPath = 'custom/themes/' . $this->theme . '/styles/' . $this->style;
        $standardPath = 'themes/' . $this->theme . '/styles/' . $this->style;
        
        if (is_file($customPath)) {
            return $customPath;
        } elseif (is_file($standardPath)) {
            return $standardPath;
        }
        return 'themes/' . $this->defaultTheme . '/styles/' . $this->defaultStyle;
    }
}
