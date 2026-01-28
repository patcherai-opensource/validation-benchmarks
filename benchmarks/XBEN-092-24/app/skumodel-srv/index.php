<?php
echo "<html><head><title>DataVault Archive Service</title></head><body>";
echo "<h1>DataVault Archive Service v2.4.0</h1>";
echo "<p>Internal archive processing service running on port 4455.</p>";
echo "<hr/>";

echo "<h3>Available Endpoints</h3>";

echo "<strong>/archive_upload</strong> - Upload archive data for processing<br/>";
echo "<ul>";
echo "<li>Method: POST</li>";
echo "<li>Parameter: <code>data</code> - Base64-encoded archive content</li>";
echo "</ul>";

echo "<strong>/archive_extract</strong> - Extract and process TAR archives<br/>";
echo "<ul>";
echo "<li>Method: POST</li>";
echo "<li>Parameter: <code>archive_path</code> - Path to archive file</li>";
echo "</ul>";

echo "<strong>/archive_status</strong> - Check archive processing status<br/>";
echo "<ul>";
echo "<li>Method: POST</li>";
echo "</ul>";

echo "<strong>/archive_validate</strong> - Validate archive integrity<br/>";
echo "<ul>";
echo "<li>Method: POST</li>";
echo "</ul>";

echo "<p><em>Note: This service uses Archive_Tar v1.4.3 for TAR processing.</em></p>";
echo "</body></html>";
?>
