<?php

/**
 * Timber Image Operations
 * 
 * Image processing operations for the Timber image service.
 * Handles conversion, resizing, and other transformations.
 */

class ImageOperationToJpg {

    private $quality;

    public function __construct($quality = 80) {
        $this->quality = $quality;
    }

    /**
     * Convert an image to JPG format.
     *
     * @param string $load_filename Source image path.
     * @param string $save_filename Destination path.
     * @return mixed
     */
    public function run($load_filename, $save_filename) {
        // Check if source file exists before processing
        if (!file_exists($load_filename)) {
            return false;
        }

        $input = imagecreatefromstring(file_get_contents($load_filename));
        if ($input === false) {
            return false;
        }

        $result = imagejpeg($input, $save_filename, $this->quality);
        imagedestroy($input);

        return $result;
    }
}

class ImageOperationResize {

    private $width;
    private $height;

    public function __construct($width, $height) {
        $this->width = $width;
        $this->height = $height;
    }

    /**
     * Resize an image to the specified dimensions.
     *
     * @param string $load_filename Source image path.
     * @param string $save_filename Destination path.
     * @return mixed
     */
    public function run($load_filename, $save_filename) {
        if (!file_exists($load_filename)) {
            return false;
        }

        $input = imagecreatefromstring(file_get_contents($load_filename));
        if ($input === false) {
            return false;
        }

        $resized = imagescale($input, $this->width, $this->height);
        $result = imagepng($resized, $save_filename);
        imagedestroy($input);
        imagedestroy($resized);

        return $result;
    }
}

class ImageOperationToWebp {

    private $quality;

    public function __construct($quality = 80) {
        $this->quality = $quality;
    }

    /**
     * Convert an image to WebP format.
     *
     * @param string $load_filename Source image path.
     * @param string $save_filename Destination path.
     * @return mixed
     */
    public function run($load_filename, $save_filename) {
        if (!file_exists($load_filename)) {
            return false;
        }

        $input = imagecreatefromstring(file_get_contents($load_filename));
        if ($input === false) {
            return false;
        }

        $result = imagewebp($input, $save_filename, $this->quality);
        imagedestroy($input);

        return $result;
    }
}

class ImageOperationLetterbox {

    private $width;
    private $height;
    private $color;

    public function __construct($width, $height, $color = '#000000') {
        $this->width = $width;
        $this->height = $height;
        $this->color = $color;
    }

    /**
     * Letterbox an image with padding.
     *
     * @param string $load_filename Source image path.
     * @param string $save_filename Destination path.
     * @return mixed
     */
    public function run($load_filename, $save_filename) {
        if (!is_file($load_filename)) {
            return false;
        }

        $input = imagecreatefromstring(file_get_contents($load_filename));
        if ($input === false) {
            return false;
        }

        $canvas = imagecreatetruecolor($this->width, $this->height);
        $rgb = sscanf($this->color, "#%02x%02x%02x");
        $bg = imagecolorallocate($canvas, $rgb[0], $rgb[1], $rgb[2]);
        imagefill($canvas, 0, 0, $bg);

        $srcW = imagesx($input);
        $srcH = imagesy($input);
        $scale = min($this->width / $srcW, $this->height / $srcH);
        $newW = (int)($srcW * $scale);
        $newH = (int)($srcH * $scale);
        $x = (int)(($this->width - $newW) / 2);
        $y = (int)(($this->height - $newH) / 2);

        imagecopyresampled($canvas, $input, $x, $y, 0, 0, $newW, $newH, $srcW, $srcH);
        $result = imagejpeg($canvas, $save_filename);
        imagedestroy($input);
        imagedestroy($canvas);

        return $result;
    }
}


/**
 * ImageHelper - Central image processing dispatcher.
 * Mirrors Timber\ImageHelper patterns.
 */
class ImageHelper {

    /**
     * Internal image operation dispatcher.
     *
     * @param string $src Source image path.
     * @param string $op  Operation name.
     * @param array  $args Operation-specific arguments.
     * @return array
     */
    public static function _operate($src, $op, $args = []) {
        $ext = pathinfo($src, PATHINFO_EXTENSION);
        $hash = md5($src . serialize($args));
        $save_dir = '/tmp/timber_cache';
        if (!is_dir($save_dir)) {
            mkdir($save_dir, 0755, true);
        }

        switch ($op) {
            case 'tojpg':
                $quality = isset($args['quality']) ? (int)$args['quality'] : 80;
                $save_filename = $save_dir . '/' . $hash . '.jpg';
                $operation = new ImageOperationToJpg($quality);
                break;
            case 'resize':
                $width = isset($args['width']) ? (int)$args['width'] : 300;
                $height = isset($args['height']) ? (int)$args['height'] : 200;
                $save_filename = $save_dir . '/' . $hash . '.png';
                $operation = new ImageOperationResize($width, $height);
                break;
            case 'towebp':
                $quality = isset($args['quality']) ? (int)$args['quality'] : 80;
                $save_filename = $save_dir . '/' . $hash . '.webp';
                $operation = new ImageOperationToWebp($quality);
                break;
            case 'letterbox':
                $width = isset($args['width']) ? (int)$args['width'] : 300;
                $height = isset($args['height']) ? (int)$args['height'] : 200;
                $color = isset($args['color']) ? $args['color'] : '#000000';
                $save_filename = $save_dir . '/' . $hash . '.jpg';
                $operation = new ImageOperationLetterbox($width, $height, $color);
                break;
            default:
                return ['status' => 'error', 'message' => 'Unknown operation: ' . $op];
        }

        $result = $operation->run($src, $save_filename);

        if ($result) {
            return [
                'status' => 'success',
                'output' => $save_filename,
                'size' => filesize($save_filename),
            ];
        }

        return ['status' => 'error', 'message' => 'Operation failed. Source file may not exist or be invalid.'];
    }

    public static function resize($src, $width, $height) {
        return self::_operate($src, 'resize', ['width' => $width, 'height' => $height]);
    }

    public static function img_to_jpg($src, $quality = 80) {
        return self::_operate($src, 'tojpg', ['quality' => $quality]);
    }

    public static function img_to_webp($src, $quality = 80) {
        return self::_operate($src, 'towebp', ['quality' => $quality]);
    }

    public static function letterbox($src, $width, $height, $color = '#000000') {
        return self::_operate($src, 'letterbox', ['width' => $width, 'height' => $height, 'color' => $color]);
    }
}
