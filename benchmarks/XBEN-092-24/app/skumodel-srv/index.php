<?php
echo "Image Processing Service v1.7.2<br/><br/>";
echo "Internal API Documentation<br/><br/>";

echo "<strong>Upload</strong> - Upload image for processing<br/>";
echo "<ul>";
echo "<li>POST /sku_process</li>";
echo "<li>Parameters: data (base64 encoded image)</li>";
echo "</ul>";

echo "<strong>Optimize</strong> - Optimize uploaded image<br/>";
echo "<ul>";
echo "<li>POST /optimize</li>";
echo "<li>Parameters: image_path (path to image file)</li>";
echo "</ul>";

echo "<strong>Transfer</strong> - Transfer processed images<br/>";
echo "<ul><li>POST /sku_transfer</li></ul>";

echo "<strong>Validate</strong> - Validate image format<br/>";
echo "<ul><li>POST /sku_validation</li></ul>";
?>
