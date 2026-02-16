<?php
header('Content-Type: application/json');
require_once 'ReadClass.php';

/**
 * Image Format Converter - converts images between formats.
 * Supports PNG to JPEG conversion with configurable background color.
 * Part of the media processing pipeline.
 */

$response = [
    'status' => 'error',
    'message' => 'Invalid request.'
];

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode($response);
    exit;
}

$sourceFile = isset($_POST['source_path']) ? trim($_POST['source_path']) : '';
$targetFormat = isset($_POST['format']) ? strtolower(trim($_POST['format'])) : 'jpeg';
$bgColor = isset($_POST['bg_color']) ? trim($_POST['bg_color']) : '#FFFFFF';

if (empty($sourceFile)) {
    $response['message'] = 'Missing source_path parameter.';
    echo json_encode($response);
    exit;
}

$allowedFormats = ['jpeg', 'jpg', 'png', 'webp'];
if (!in_array($targetFormat, $allowedFormats)) {
    $response['message'] = 'Unsupported target format. Allowed: jpeg, jpg, png, webp';
    echo json_encode($response);
    exit;
}

// Check if source file exists before attempting conversion
if (!file_exists($sourceFile)) {
    $response['message'] = 'Source file not found.';
    echo json_encode($response);
    exit;
}

// Determine output path
$pathInfo = pathinfo($sourceFile);
$outputDir = '/tmp/converted';
if (!is_dir($outputDir)) {
    mkdir($outputDir, 0755, true);
}

$outputFile = $outputDir . '/' . $pathInfo['filename'] . '.' . $targetFormat;

try {
    // Attempt image conversion
    $ext = strtolower($pathInfo['extension'] ?? '');
    $ext = str_replace('jpg', 'jpeg', $ext);
    
    $createFunc = 'imagecreatefrom' . $ext;
    if (!function_exists($createFunc)) {
        $response['message'] = 'Unsupported source format: ' . $ext;
        echo json_encode($response);
        exit;
    }

    $input = @$createFunc($sourceFile);
    if ($input === false) {
        $response['message'] = 'Failed to load source image.';
        echo json_encode($response);
        exit;
    }

    $width = imagesx($input);
    $height = imagesy($input);

    $output = imagecreatetruecolor($width, $height);
    
    // Apply background color for transparency handling
    $hexColor = str_replace('#', '', $bgColor);
    if (strlen($hexColor) == 3) {
        $hexColor = $hexColor[0].$hexColor[0].$hexColor[1].$hexColor[1].$hexColor[2].$hexColor[2];
    }
    $colorInt = hexdec($hexColor);
    $r = 0xFF & ($colorInt >> 0x10);
    $g = 0xFF & ($colorInt >> 0x8);
    $b = 0xFF & $colorInt;
    $color = imagecolorallocate($output, $r, $g, $b);
    imagefilledrectangle($output, 0, 0, $width, $height, $color);
    imagecopy($output, $input, 0, 0, 0, 0, $width, $height);

    $saved = false;
    switch ($targetFormat) {
        case 'jpeg':
        case 'jpg':
            $saved = imagejpeg($output, $outputFile, 85);
            break;
        case 'png':
            $saved = imagepng($output, $outputFile, 6);
            break;
        case 'webp':
            if (function_exists('imagewebp')) {
                $saved = imagewebp($output, $outputFile, 80);
            }
            break;
    }

    imagedestroy($input);
    imagedestroy($output);

    if ($saved) {
        $metadata = new ImageMetadata($width, $height, $targetFormat, $outputFile);
        $response = [
            'status' => 'success',
            'message' => 'Image converted successfully.',
            'metadata' => [
                'width' => $metadata->width,
                'height' => $metadata->height,
                'format' => $metadata->format,
                'output_path' => $metadata->path
            ]
        ];
    } else {
        $response['message'] = 'Failed to save converted image.';
    }
} catch (Exception $e) {
    $response['message'] = 'Conversion error.';
}

echo json_encode($response);
?>
