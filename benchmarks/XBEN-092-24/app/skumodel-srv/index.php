<?php
echo "Timber Image Processing Service v1.23.0<br/><br/>";
echo "Internal image processing API for product catalog management.<br/><br/>";

echo "<strong>Upload</strong> - Upload an image for processing<br/>";
echo "<ul>";
echo "<li>Method: POST</li>";
echo "<li>Parameters: data (base64-encoded image), ext (file extension)</li>";
echo "<li>Endpoint: /sku_process</li>";
echo "</ul>";

echo "<strong>Image Operations</strong> - Process uploaded images<br/>";
echo "<ul>";
echo "<li>Method: POST</li>";
echo "<li>Parameters: src (image path), operation (tojpg|resize|towebp|letterbox), width, height, quality</li>";
echo "<li>Endpoint: /image_operate</li>";
echo "</ul>";

echo "<strong>Transfer</strong> - View SKU transfer records<br/>";
echo "<ul><li>Endpoint: /sku_transfer</li></ul>";

echo "<strong>Validate</strong> - Validate a SKU number<br/>";
echo "<ul><li>Endpoint: /sku_validation</li></ul>";
?>
