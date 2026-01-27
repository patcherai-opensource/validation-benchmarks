<?php
echo "Image Optimization Service v1.7.2<br/><br/>" .
     "API Documentation - Internal Use Only<br/><br/>";

echo "<strong>Upload</strong> - Upload image for optimization<br/>";
echo "<ul>";
echo "<li>POST /upload - Upload base64-encoded image data</li>";
echo "<li>Parameters: data (base64 encoded image)</li>";
echo "</ul>";

echo "<strong>Optimize</strong> - Optimize an uploaded image<br/>";
echo "<ul><li>POST /optimize - Optimize image at specified path</li></ul>";
echo "<li>Parameters: path_to_image (file path to image)</li>";

echo "<strong>Status</strong> - Check optimization queue status<br/>";
echo "<ul><li>POST /status</li></ul>";
?>
