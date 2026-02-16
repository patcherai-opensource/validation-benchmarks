<?php

class ThemeResolver {

    private $skin;
    private $layout;
    private $appearance;
    private $layoutContent;
    private $defaults;

    public function __construct() {
        $this->defaults = array(
            'skin' => 'developer',
            'layout' => 'default.html',
            'appearance' => 'developer.css'
        );
        $this->skin = null;
        $this->layout = null;
        $this->appearance = null;
        $this->layoutContent = null;

        $this->resolveThemeSettings();
    }

    private function resolveThemeSettings() {
        if (isset($_REQUEST['skin']) && isset($_REQUEST['appearance']) && isset($_REQUEST['layout'])) {
            $requestedSkin = $_REQUEST['skin'];
            $requestedAppearance = $_REQUEST['appearance'];
            $requestedLayout = $_REQUEST['layout'];

            if (
                (is_dir('custom/skins/' . $requestedSkin) || is_dir('skins/' . $requestedSkin))
                && (is_file('custom/skins/' . $requestedSkin . '/styles/' . $requestedAppearance) || is_file('skins/' . $requestedSkin . '/styles/' . $requestedAppearance))
                && (is_file('custom/skins/' . $requestedSkin . '/layouts/' . $requestedLayout) || is_file('skins/' . $requestedSkin . '/layouts/' . $requestedLayout))
            ) {
                $this->skin = $requestedSkin;
                $this->appearance = $requestedAppearance;
                $this->layout = $requestedLayout;
            } else {
                $this->skin = $this->defaults['skin'];
                $this->appearance = $this->defaults['appearance'];
                $this->layout = $this->defaults['layout'];
            }
        } else {
            $this->skin = $this->defaults['skin'];
            $this->appearance = $this->defaults['appearance'];
            $this->layout = $this->defaults['layout'];
        }
    }

    public function resolveLayout() {
        $skinPath = 'skins/' . $this->skin;
        $filePath = $skinPath . '/layouts/' . $this->layout;

        if (!(file_exists('custom/' . $skinPath) || file_exists($skinPath))) {
            return null;
        }

        if (!(file_exists('custom/' . $filePath) || file_exists($filePath))) {
            return null;
        }

        $resolvedPath = file_exists('custom/' . $filePath) ? 'custom/' . $filePath : $filePath;

        $content = file_get_contents($resolvedPath);
        if ($content === false) {
            return null;
        }

        $this->layoutContent = $content;
        return $content;
    }

    public function getStylesheet() {
        $stylePath = 'skins/' . $this->skin . '/styles/' . $this->appearance;
        $resolvedStyle = file_exists('custom/' . $stylePath) ? 'custom/' . $stylePath : $stylePath;

        if (file_exists($resolvedStyle)) {
            $cssContent = file_get_contents($resolvedStyle);
            return '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">' . "\n" .
                   '<style>' . $cssContent . '</style>';
        }

        return '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">';
    }

    public function getSkin() {
        return $this->skin;
    }

    public function getLayout() {
        return $this->layout;
    }

    public function getAppearance() {
        return $this->appearance;
    }
}
