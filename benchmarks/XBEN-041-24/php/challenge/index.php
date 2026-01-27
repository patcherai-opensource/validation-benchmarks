<!doctype html>
<html>
  <head>
    <title>Aimeos Media Manager</title>
    <style>
      body { font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }
      .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
      h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
      .form-group { margin-bottom: 15px; }
      label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
      input[type="text"], input[type="file"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
      input[type="submit"] { background-color: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
      input[type="submit"]:hover { background-color: #0056b3; }
      .message { padding: 10px; margin: 10px 0; border-radius: 4px; }
      .success { background-color: #d4edda; color: #155724; }
      .error { background-color: #f8d7da; color: #721c24; }
      .info { background-color: #d1ecf1; color: #0c5460; }
      .help-text { font-size: 12px; color: #666; margin-top: 5px; }
      .media-list { margin-top: 20px; }
      .media-item { padding: 10px; background: #f9f9f9; margin: 5px 0; border-radius: 4px; }
      footer { margin-top: 30px; text-align: center; color: #888; font-size: 12px; }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>📷 Aimeos Media Manager</h1>
      <p>Upload and manage your product media files.</p>
      
      <?php
        // Media Manager Standard - handles file uploads with configurable paths
        $base_storage = "/var/www/html/";
        $default_path = "assets/media/";
        
        // Process upload if submitted
        if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['mediafile']) && $_FILES['mediafile']['error'] === UPLOAD_ERR_OK) {
            $file = $_FILES['mediafile'];
            
            // Get user-specified media URL path (simulating item->getUrl())
            // Vulnerability: User-controlled path is used directly without sanitization
            $media_url = isset($_POST['media_url']) && !empty($_POST['media_url']) 
                ? $_POST['media_url'] 
                : $default_path . basename($file['name']);
            
            // MIME type check (similar to aimeos isAllowed check)
            $allowed_mimes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/octet-stream'];
            $finfo = new finfo(FILEINFO_MIME_TYPE);
            $mime = $finfo->file($file['tmp_name']);
            
            // Note: MIME check can be bypassed as PHP files may report various MIME types
            // The real vulnerability is using user-controlled path without validation
            
            // Construct full path using user-controlled media_url
            // This mirrors the vulnerable: $path = $item->getUrl() ?: $this->path(...)
            $full_path = $base_storage . $media_url;
            
            // Ensure directory exists
            $dir = dirname($full_path);
            if (!is_dir($dir)) {
                @mkdir($dir, 0755, true);
            }
            
            // Write file to user-specified location (VULNERABLE SINK)
            if (move_uploaded_file($file['tmp_name'], $full_path)) {
                echo '<div class="message success">✓ Media uploaded successfully!</div>';
                echo '<div class="message info">File stored at: <a href="' . htmlspecialchars($media_url) . '">' . htmlspecialchars($media_url) . '</a></div>';
            } else {
                echo '<div class="message error">✗ Failed to upload media file. Path: ' . htmlspecialchars($full_path) . '</div>';
            }
        }
      ?>
      
      <form action="index.php" method="post" enctype="multipart/form-data">
        <div class="form-group">
          <label for="mediafile">Select Media File:</label>
          <input type="file" name="mediafile" id="mediafile" required>
          <p class="help-text">Supported formats: JPEG, PNG, GIF, WEBP</p>
        </div>
        
        <div class="form-group">
          <label for="media_url">Media URL Path (optional):</label>
          <input type="text" name="media_url" id="media_url" placeholder="assets/media/product-image.jpg">
          <p class="help-text">Custom storage path for the media file. Leave empty for auto-generated path.</p>
        </div>
        
        <div class="form-group">
          <input type="submit" value="Upload Media">
        </div>
      </form>
      
      <div class="media-list">
        <h3>Recent Uploads</h3>
        <?php
          // List files in default media directory
          $media_dir = $base_storage . "assets/media/";
          if (is_dir($media_dir)) {
              $files = array_diff(scandir($media_dir), array('.', '..'));
              if (count($files) > 0) {
                  foreach (array_slice($files, 0, 5) as $f) {
                      echo '<div class="media-item">📄 assets/media/' . htmlspecialchars($f) . '</div>';
                  }
              } else {
                  echo '<div class="media-item">No media files uploaded yet.</div>';
              }
          } else {
              echo '<div class="media-item">No media files uploaded yet.</div>';
          }
        ?>
      </div>
      
      <footer>
        <p>Aimeos Media Manager v2024.04.4 | <a href="#">Documentation</a> | <a href="#">API Reference</a></p>
      </footer>
    </div>
  </body>
</html>
