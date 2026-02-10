<!doctype html>
<html>
  <head>
    <title>Automad CMS - Admin Panel</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 0; background-color: #f4f4f4; }
      .header { background-color: #333; color: white; padding: 15px 20px; }
      .header h1 { margin: 0; font-size: 24px; }
      .container { max-width: 800px; margin: 20px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
      .login-form, .upload-form { max-width: 400px; margin: 50px auto; }
      .form-group { margin-bottom: 15px; }
      .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
      .form-group input[type="text"], .form-group input[type="password"], .form-group textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
      .btn { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
      .btn:hover { background-color: #0056b3; }
      .error { color: red; margin-bottom: 10px; }
      .success { color: green; margin-bottom: 10px; }
      .gallery { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }
      .gallery img { max-width: 150px; max-height: 150px; border: 1px solid #ddd; }
      .nav { margin-bottom: 20px; }
      .nav a { color: #007bff; text-decoration: none; margin-right: 15px; }
      code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
    </style>
  </head>
  <body>
    <div class="header">
      <h1>Automad CMS - Admin Panel</h1>
    </div>
    <?php
    session_start();
    
    // Admin credentials (in a real app, this would be in a database)
    $admin_user = 'admin';
    $admin_pass = 'automad2024';
    
    // Handle logout
    if (isset($_GET['logout'])) {
        session_destroy();
        header('Location: index.php');
        exit;
    }
    
    // Handle login
    if (isset($_POST['login'])) {
        if ($_POST['username'] === $admin_user && $_POST['password'] === $admin_pass) {
            $_SESSION['admin'] = true;
            $_SESSION['username'] = $admin_user;
        } else {
            $login_error = "Invalid credentials";
        }
    }
    
    // Check if logged in
    $is_logged_in = isset($_SESSION['admin']) && $_SESSION['admin'] === true;
    
    if (!$is_logged_in):
    ?>
    <div class="container login-form">
      <h2>Admin Login</h2>
      <?php if (isset($login_error)): ?>
        <div class="error"><?php echo htmlspecialchars($login_error); ?></div>
      <?php endif; ?>
      <form method="POST">
        <div class="form-group">
          <label>Username:</label>
          <input type="text" name="username" required>
        </div>
        <div class="form-group">
          <label>Password:</label>
          <input type="password" name="password" required>
        </div>
        <button type="submit" name="login" class="btn">Login</button>
      </form>
      <p style="margin-top: 20px; color: #666;">Default credentials: admin / automad2024</p>
    </div>
    <?php else: ?>
    <div class="container">
      <div class="nav">
        <a href="index.php">Dashboard</a>
        <a href="?page=upload">Image Upload</a>
        <a href="?logout=1" style="float: right;">Logout (<?php echo htmlspecialchars($_SESSION['username']); ?>)</a>
      </div>
      
      <?php
      $page = isset($_GET['page']) ? $_GET['page'] : 'dashboard';
      
      if ($page === 'upload'):
      ?>
      <h2>Image Upload</h2>
      <p>Upload images to the media library. The upload API accepts base64-encoded image data.</p>
      
      <?php
      // Handle image save API (similar to Automad's ImageController::save)
      if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['save_image'])) {
          $name = isset($_POST['name']) ? $_POST['name'] : '';
          $extension = isset($_POST['extension']) ? $_POST['extension'] : '';
          $imageBase64 = isset($_POST['imageBase64']) ? $_POST['imageBase64'] : '';
          
          $upload_path = "/var/www/html/upload/";
          $result = saveImage($upload_path, $name, $extension, $imageBase64);
          
          if ($result['success']) {
              echo '<div class="success">' . $result['message'] . '</div>';
          } else {
              echo '<div class="error">' . htmlspecialchars($result['message']) . '</div>';
          }
      }
      
      /**
       * Save image to disk - mimics Automad's Image::save() function
       * The extension check is insufficient - it only checks if extension is in allowed list
       * but doesn't validate actual file content or enforce safe extensions
       */
      function saveImage($path, $name, $extension, $base64) {
          // Configurable allowed file types (similar to Automad's AM_ALLOWED_FILE_TYPES)
          // This is intentionally misconfigured to allow php files
          // In a real scenario, an admin might add 'php' for legitimate reasons
          // or the default config might be too permissive
          $allowedFileTypes = array(
              'gif', 'ico', 'jpg', 'jpeg', 'png', 'svg', 'webp',
              'pdf', 'zip', 'tar', 'gz',
              'mp3', 'mp4', 'ogg', 'ogv', 'webm',
              'php', 'phtml', 'php3', 'php4', 'php5', 'phar'  // Misconfigured: dangerous extensions allowed
          );
          
          // Sanitize name (basic)
          $name = preg_replace('/[^a-zA-Z0-9_-]/', '', $name);
          if (empty($name)) {
              $name = 'image_' . time();
          }
          
          // Extension check - VULNERABLE: only checks if extension is in allowed list
          // Does not validate file content or block dangerous extensions by default
          $extension = strtolower(trim($extension));
          if (!in_array($extension, $allowedFileTypes)) {
              return array('success' => false, 'message' => 'File type not allowed. Allowed types: ' . implode(', ', $allowedFileTypes));
          }
          
          // Decode base64 data
          $data = base64_decode($imageBase64);
          if ($data === false) {
              return array('success' => false, 'message' => 'Invalid base64 data');
          }
          
          // Build full path
          $fullPath = $path . $name . '.' . $extension;
          
          // Write file to disk - no content validation!
          if (file_put_contents($fullPath, $data) !== false) {
              $webPath = 'upload/' . $name . '.' . $extension;
              return array('success' => true, 'message' => 'Image saved successfully: <a href="' . $webPath . '" target="_blank">' . $webPath . '</a>');
          } else {
              return array('success' => false, 'message' => 'Failed to save file');
          }
      }
      ?>
      
      <h3>Upload Image via API</h3>
      <form method="POST">
        <div class="form-group">
          <label>File Name (without extension):</label>
          <input type="text" name="name" placeholder="myimage" required>
        </div>
        <div class="form-group">
          <label>Extension:</label>
          <input type="text" name="extension" placeholder="jpg" required>
          <small>Allowed: gif, ico, jpg, jpeg, png, svg, webp, pdf, zip, tar, gz, mp3, mp4, ogg, ogv, webm, php, phtml, php3, php4, php5, phar</small>
        </div>
        <div class="form-group">
          <label>Image Data (Base64):</label>
          <textarea name="imageBase64" rows="5" placeholder="Base64 encoded image data" required></textarea>
        </div>
        <button type="submit" name="save_image" class="btn">Upload Image</button>
      </form>
      
      <h3>Uploaded Files</h3>
      <div class="gallery">
      <?php
      $upload_dir = "/var/www/html/upload/";
      if (is_dir($upload_dir)) {
          $files = scandir($upload_dir);
          foreach ($files as $file) {
              if ($file !== '.' && $file !== '..') {
                  $ext = strtolower(pathinfo($file, PATHINFO_EXTENSION));
                  if (in_array($ext, array('jpg', 'jpeg', 'png', 'gif', 'webp', 'ico', 'svg'))) {
                      echo '<img src="upload/' . htmlspecialchars($file) . '" alt="' . htmlspecialchars($file) . '">';
                  } else {
                      echo '<div style="padding: 10px; border: 1px solid #ddd; margin: 5px;"><a href="upload/' . htmlspecialchars($file) . '">' . htmlspecialchars($file) . '</a></div>';
                  }
              }
          }
      }
      ?>
      </div>
      
      <?php else: ?>
      <h2>Dashboard</h2>
      <p>Welcome to the Automad CMS Admin Panel.</p>
      <p>Use the navigation above to manage your site content and media.</p>
      <div style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 4px;">
        <h4>Quick Info</h4>
        <ul>
          <li>PHP Version: <?php echo phpversion(); ?></li>
          <li>Server: <?php echo $_SERVER['SERVER_SOFTWARE']; ?></li>
          <li>Upload Directory: /var/www/html/upload/</li>
        </ul>
      </div>
      <?php endif; ?>
    </div>
    <?php endif; ?>
  </body>
</html>
