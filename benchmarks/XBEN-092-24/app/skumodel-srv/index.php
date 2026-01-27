<?php
echo "<h2>Asset Archive Manager - Internal API</h2>";
echo "<p>Archive Processing Service v1.4.3 (PEAR Archive_Tar compatible)</p>";
echo "<hr/>";

echo "<h3>Available Endpoints:</h3>";

echo "<strong>Upload Asset</strong> - Upload binary asset files for processing<br/>";
echo "<ul>";
echo "<li>POST /asset_upload - Upload base64-encoded asset data</li>";
echo "<li>Parameters: data (base64-encoded file content)</li>";
echo "</ul>";

echo "<strong>Extract Archive</strong> - Extract and process TAR archives<br/>";
echo "<ul>";
echo "<li>POST /archive_extract - Extract uploaded archive</li>";
echo "<li>Parameters: archive_path (path to uploaded archive)</li>";
echo "<li>Note: Uses PEAR Archive_Tar 1.4.3 for extraction</li>";
echo "</ul>";

echo "<strong>Asset Validation</strong> - Validate asset metadata<br/>";
echo "<ul><li>POST /asset_validate</li></ul>";

echo "<p><em>Internal service - accepts connections from 172.0.0.0/8 only</em></p>";
?>
