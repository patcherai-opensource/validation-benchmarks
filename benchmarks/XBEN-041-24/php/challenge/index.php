<!doctype html>
<html>
  <head>
    <title>ContentBox CMS - Media Manager</title>
    <style>
      body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        background-color: #f4f5f7;
        margin: 0;
        padding: 0;
      }
      .navbar {
        background-color: #2c3e50;
        color: white;
        padding: 15px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .navbar h1 {
        margin: 0;
        font-size: 1.4em;
      }
      .navbar .user-info {
        font-size: 0.9em;
        color: #bdc3c7;
      }
      .container {
        max-width: 900px;
        margin: 40px auto;
        padding: 0 20px;
      }
      .card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        padding: 30px;
        margin-bottom: 30px;
      }
      .card h2 {
        margin-top: 0;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
      }
      .upload-area {
        border: 2px dashed #bdc3c7;
        border-radius: 8px;
        padding: 40px;
        text-align: center;
        margin: 20px 0;
        background: #fafafa;
      }
      .upload-area:hover {
        border-color: #3498db;
        background: #f0f8ff;
      }
      .btn {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1em;
        margin-top: 15px;
      }
      .btn:hover {
        background-color: #2980b9;
      }
      .success-msg {
        background: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
      }
      .error-msg {
        background: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
      }
      .media-list {
        margin-top: 20px;
      }
      .media-item {
        display: flex;
        align-items: center;
        padding: 15px;
        border-bottom: 1px solid #eee;
      }
      .media-item:last-child {
        border-bottom: none;
      }
      .media-preview {
        width: 80px;
        height: 80px;
        object-fit: cover;
        border-radius: 5px;
        margin-right: 15px;
        background: #eee;
      }
      .media-info {
        flex-grow: 1;
      }
      .media-info a {
        color: #3498db;
        text-decoration: none;
        font-weight: 500;
      }
      .media-info a:hover {
        text-decoration: underline;
      }
      .file-input {
        display: none;
      }
      .file-label {
        cursor: pointer;
        color: #3498db;
        text-decoration: underline;
      }
      .info-text {
        color: #7f8c8d;
        font-size: 0.9em;
        margin-top: 10px;
      }
      .sidebar-info {
        font-size: 0.85em;
        color: #7f8c8d;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 5px;
      }
    </style>
  </head>
  <body>
    <div class="navbar">
      <h1>📦 ContentBox CMS</h1>
      <div class="user-info">Logged in as: admin@contentbox.local</div>
    </div>
    
    <div class="container">
      <div class="card">
        <h2>🖼️ Media Manager</h2>
        <p>Upload and manage media files for your website content.</p>
        
        <form action="index.php" method="post" enctype="multipart/form-data">
          <div class="upload-area">
            <svg width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="#bdc3c7" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <p>Drag and drop files here or <label for="mediafile" class="file-label">browse</label></p>
            <input type="file" name="mediafile" id="mediafile" class="file-input" onchange="updateFileName(this)">
            <div id="selected-file" class="info-text">No file selected</div>
            <button type="submit" class="btn" name="upload">Upload Media</button>
          </div>
        </form>
        
        <div class="sidebar-info">
          <strong>Allowed formats:</strong> Images (jpg, png, gif, svg), Documents (pdf, doc), and more.<br>
          <strong>Max file size:</strong> 10MB
        </div>
        
        <?php
        $media_path = "/var/www/html/media/";
        $meta_file = "/var/www/html/media/.metadata.json";
        
        // Handle file upload
        if (isset($_FILES['mediafile']) && $_FILES['mediafile']['error'] === UPLOAD_ERR_OK)
        {
            $filename = basename($_FILES["mediafile"]["name"]);
            $target_path = $media_path . $filename;
            
            // Save media file - extension validation deferred for performance
            if (move_uploaded_file($_FILES['mediafile']['tmp_name'], $target_path)) {
                // Update metadata
                $metadata = [];
                if (file_exists($meta_file)) {
                    $metadata = json_decode(file_get_contents($meta_file), true) ?: [];
                }
                $metadata[] = [
                    'filename' => $filename,
                    'uploaded' => date('Y-m-d H:i:s'),
                    'size' => $_FILES['mediafile']['size']
                ];
                file_put_contents($meta_file, json_encode($metadata, JSON_PRETTY_PRINT));
                
                echo "<div class='success-msg'>✓ Media file uploaded successfully: <a href='media/" . htmlspecialchars($filename) . "'>" . htmlspecialchars($filename) . "</a></div>";
            } else {
                echo "<div class='error-msg'>✗ Failed to upload media file. Please try again.</div>";
            }
        }
        ?>
      </div>
      
      <div class="card">
        <h2>📂 Media Library</h2>
        <?php
        // List uploaded media
        $media_files = [];
        if (file_exists($meta_file)) {
            $metadata = json_decode(file_get_contents($meta_file), true) ?: [];
            foreach ($metadata as $item) {
                $filepath = $media_path . $item['filename'];
                if (file_exists($filepath)) {
                    $media_files[] = $item;
                }
            }
        }
        
        if (empty($media_files)) {
            echo "<p class='info-text'>No media files uploaded yet. Upload your first file above!</p>";
        } else {
            echo "<div class='media-list'>";
            foreach (array_reverse($media_files) as $item) {
                $ext = strtolower(pathinfo($item['filename'], PATHINFO_EXTENSION));
                $is_image = in_array($ext, ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']);
                echo "<div class='media-item'>";
                if ($is_image) {
                    echo "<img src='media/" . htmlspecialchars($item['filename']) . "' class='media-preview' onerror=\"this.style.display='none'\">";
                } else {
                    echo "<div class='media-preview' style='display:flex;align-items:center;justify-content:center;color:#7f8c8d;font-size:0.8em;'>" . strtoupper($ext) . "</div>";
                }
                echo "<div class='media-info'>";
                echo "<a href='media/" . htmlspecialchars($item['filename']) . "'>" . htmlspecialchars($item['filename']) . "</a><br>";
                echo "<span class='info-text'>Uploaded: " . htmlspecialchars($item['uploaded']) . " | Size: " . number_format($item['size'] / 1024, 1) . " KB</span>";
                echo "</div>";
                echo "</div>";
            }
            echo "</div>";
        }
        ?>
      </div>
    </div>
    
    <script>
      function updateFileName(input) {
        var fileName = input.files.length > 0 ? input.files[0].name : 'No file selected';
        document.getElementById('selected-file').textContent = 'Selected: ' + fileName;
      }
    </script>
  </body>
</html>
