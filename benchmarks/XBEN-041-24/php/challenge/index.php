<?php
session_start();

// Simple authentication check
function isAuthenticated() {
    return isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;
}

// Handle login
if (isset($_POST['login'])) {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    // Simple auth - any valid credentials work (simulating low-privilege user)
    if ($username === 'editor' && $password === 'editor123') {
        $_SESSION['authenticated'] = true;
        $_SESSION['username'] = $username;
    }
}

// Handle logout
if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: /');
    exit;
}
?>
<!doctype html>
<html>
  <head>
    <title>Aimeos Media Manager</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="password"], input[type="file"] { padding: 8px; width: 300px; border: 1px solid #ddd; border-radius: 4px; }
        button, input[type="submit"] { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover, input[type="submit"]:hover { background: #0056b3; }
        .alert { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-error { background: #f8d7da; color: #721c24; }
        .alert-info { background: #cce5ff; color: #004085; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; color: #007bff; text-decoration: none; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Aimeos Media Manager</h1>
      
      <?php if (!isAuthenticated()): ?>
        <!-- Login Form -->
        <div class="alert alert-info">
            Please login to access the media manager. Use credentials: <code>editor / editor123</code>
        </div>
        <form method="post">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" name="login">Login</button>
        </form>
      <?php else: ?>
        <!-- Authenticated Content -->
        <div class="nav">
            <span>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?>!</span>
            <a href="?logout">Logout</a>
        </div>
        
        <?php
        // Initialize media items storage
        if (!isset($_SESSION['media_items'])) {
            $_SESSION['media_items'] = [];
        }
        
        $message = '';
        $error = '';
        
        // Handle media item creation/update
        if (isset($_POST['create_media'])) {
            $label = $_POST['media_label'] ?? '';
            $url = $_POST['media_url'] ?? '';  // User-controlled path - VULNERABLE
            
            if ($label && $url) {
                $id = count($_SESSION['media_items']) + 1;
                $_SESSION['media_items'][$id] = [
                    'id' => $id,
                    'label' => $label,
                    'url' => $url,  // Storing user-controlled path
                    'uploaded' => false
                ];
                $message = "Media item created with ID: $id";
            }
        }
        
        // Handle file upload - VULNERABLE: uses user-controlled path from media.url
        if (isset($_POST['upload_media']) && isset($_FILES['media_file'])) {
            $mediaId = intval($_POST['media_id']);
            
            if (isset($_SESSION['media_items'][$mediaId])) {
                $item = $_SESSION['media_items'][$mediaId];
                $file = $_FILES['media_file'];
                
                // Check MIME type (mimics the CVE's isAllowed check)
                $allowedMimes = ['image/jpeg', 'image/png', 'image/gif', 'text/plain', 'application/octet-stream'];
                $mime = mime_content_type($file['tmp_name']);
                
                // VULNERABILITY: If media.url is set, use it as the path
                // This mirrors the CVE: $path = $item->getUrl() ?: $this->path(...)
                if (!empty($item['url'])) {
                    $path = '/var/www/html/' . $item['url'];  // User-controlled path!
                } else {
                    // Generate safe path (what the fix does)
                    $ext = pathinfo($file['name'], PATHINFO_EXTENSION);
                    $safeName = uniqid() . '.' . $ext;
                    $path = '/var/www/html/upload/' . $safeName;
                }
                
                // Ensure directory exists
                $dir = dirname($path);
                if (!is_dir($dir)) {
                    @mkdir($dir, 0755, true);
                }
                
                // Write file to user-controlled path
                if (move_uploaded_file($file['tmp_name'], $path)) {
                    $_SESSION['media_items'][$mediaId]['uploaded'] = true;
                    $_SESSION['media_items'][$mediaId]['actual_path'] = $path;
                    $message = "File uploaded successfully to: " . htmlspecialchars($item['url'] ?: basename($path));
                } else {
                    $error = "Failed to upload file";
                }
            } else {
                $error = "Media item not found";
            }
        }
        
        if ($message): ?>
            <div class="alert alert-success"><?php echo $message; ?></div>
        <?php endif;
        
        if ($error): ?>
            <div class="alert alert-error"><?php echo $error; ?></div>
        <?php endif; ?>
        
        <h2>Create Media Item</h2>
        <p>Create a media item first, then upload a file to it.</p>
        <form method="post">
            <div class="form-group">
                <label>Media Label:</label>
                <input type="text" name="media_label" placeholder="My Image" required>
            </div>
            <div class="form-group">
                <label>Media URL (storage path):</label>
                <input type="text" name="media_url" placeholder="upload/image.jpg" required>
                <small style="color: #666;">Specify where the file will be stored</small>
            </div>
            <button type="submit" name="create_media">Create Media Item</button>
        </form>
        
        <h2>Media Items</h2>
        <?php if (empty($_SESSION['media_items'])): ?>
            <p>No media items yet. Create one above.</p>
        <?php else: ?>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Label</th>
                    <th>URL Path</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
                <?php foreach ($_SESSION['media_items'] as $item): ?>
                <tr>
                    <td><?php echo $item['id']; ?></td>
                    <td><?php echo htmlspecialchars($item['label']); ?></td>
                    <td><code><?php echo htmlspecialchars($item['url']); ?></code></td>
                    <td><?php echo $item['uploaded'] ? '✓ Uploaded' : 'Pending'; ?></td>
                    <td>
                        <?php if (!$item['uploaded']): ?>
                        <form method="post" enctype="multipart/form-data" style="display:inline;">
                            <input type="hidden" name="media_id" value="<?php echo $item['id']; ?>">
                            <input type="file" name="media_file" required>
                            <button type="submit" name="upload_media">Upload</button>
                        </form>
                        <?php else: ?>
                            <a href="/<?php echo htmlspecialchars($item['url']); ?>" target="_blank">View</a>
                        <?php endif; ?>
                    </td>
                </tr>
                <?php endforeach; ?>
            </table>
        <?php endif; ?>
        
      <?php endif; ?>
    </div>
  </body>
</html>
