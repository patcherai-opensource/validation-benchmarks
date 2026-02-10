<?php
session_start();

if (!isset($_SESSION['admin_authenticated']) || $_SESSION['admin_authenticated'] !== true) {
    header('Location: /admin/login.php');
    exit;
}

$upload_dir = '/var/www/html/uploads/';
$message = '';
$message_type = '';

$allowed_types = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'ico', 'bmp', 'tiff'];

function isAllowedExtension($ext, $allowed) {
    $ext = strtolower(trim($ext));
    foreach ($allowed as $allowed_ext) {
        if (strpos($ext, $allowed_ext) !== false) {
            return true;
        }
    }
    return false;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'save') {
    $name = $_POST['name'] ?? '';
    $extension = $_POST['extension'] ?? '';
    $imageBase64 = $_POST['imageBase64'] ?? '';
    
    if (empty($name) || empty($extension) || empty($imageBase64)) {
        $message = 'All fields are required';
        $message_type = 'error';
    } else {
        $name = preg_replace('/[^a-zA-Z0-9_-]/', '', $name);
        
        $extension = trim($extension);
        $extension = ltrim($extension, '.');
        
        if (!isAllowedExtension($extension, $allowed_types)) {
            $message = 'File type not allowed. Permitted types: ' . implode(', ', $allowed_types);
            $message_type = 'error';
        } else {
            $decoded = base64_decode($imageBase64);
            if ($decoded === false) {
                $message = 'Invalid base64 data';
                $message_type = 'error';
            } else {
                $filename = $name . '.' . $extension;
                $filepath = $upload_dir . $filename;
                
                if (file_put_contents($filepath, $decoded) !== false) {
                    $message = 'Image saved successfully as ' . htmlspecialchars($filename);
                    $message_type = 'success';
                } else {
                    $message = 'Failed to save image';
                    $message_type = 'error';
                }
            }
        }
    }
}

$images = [];
if (is_dir($upload_dir)) {
    $files = scandir($upload_dir);
    foreach ($files as $file) {
        if ($file !== '.' && $file !== '..') {
            $images[] = $file;
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Images - Automad</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f5f5; }
        .header { background: #1a1a2e; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5rem; font-weight: 500; }
        .nav { display: flex; gap: 2rem; align-items: center; }
        .nav a { color: #ccc; text-decoration: none; font-size: 0.9rem; }
        .nav a:hover { color: white; }
        .user-info { color: #aaa; font-size: 0.85rem; }
        .layout { display: flex; min-height: calc(100vh - 60px); }
        .sidebar { width: 250px; background: #fff; border-right: 1px solid #e0e0e0; padding: 1.5rem; }
        .sidebar h3 { font-size: 0.75rem; text-transform: uppercase; color: #999; margin-bottom: 1rem; letter-spacing: 0.5px; }
        .sidebar ul { list-style: none; }
        .sidebar li { margin-bottom: 0.5rem; }
        .sidebar a { color: #333; text-decoration: none; font-size: 0.9rem; padding: 0.5rem; display: block; border-radius: 4px; }
        .sidebar a:hover, .sidebar a.active { background: #f0f0f0; }
        .main { flex: 1; padding: 2rem; }
        .card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem; }
        .card h2 { margin-bottom: 1rem; color: #333; font-size: 1.2rem; }
        .form-row { display: flex; gap: 1rem; margin-bottom: 1rem; }
        .form-group { flex: 1; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-size: 0.9rem; color: #333; font-weight: 500; }
        .form-group input, .form-group textarea { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem; }
        .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #4a4a8a; }
        .form-group textarea { min-height: 100px; font-family: monospace; }
        .form-group small { display: block; margin-top: 0.25rem; color: #999; font-size: 0.8rem; }
        .btn { padding: 0.75rem 1.5rem; background: #4a4a8a; color: white; border: none; border-radius: 4px; font-size: 0.9rem; cursor: pointer; }
        .btn:hover { background: #3a3a7a; }
        .message { padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .message.success { background: #d4edda; color: #155724; }
        .message.error { background: #f8d7da; color: #721c24; }
        .image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem; }
        .image-item { background: #f8f8f8; border-radius: 4px; padding: 0.5rem; text-align: center; }
        .image-item img { max-width: 100%; height: auto; border-radius: 4px; }
        .image-item p { margin-top: 0.5rem; font-size: 0.8rem; color: #666; word-break: break-all; }
        .image-item a { color: #4a4a8a; text-decoration: none; }
        .image-item a:hover { text-decoration: underline; }
        .dropzone { border: 2px dashed #ddd; border-radius: 8px; padding: 2rem; text-align: center; cursor: pointer; transition: border-color 0.2s; margin-bottom: 1rem; }
        .dropzone:hover, .dropzone.dragover { border-color: #4a4a8a; }
        .dropzone p { color: #666; }
        .preview { max-width: 200px; margin: 1rem auto; }
        .preview img { max-width: 100%; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Automad Dashboard</h1>
        <nav class="nav">
            <a href="/">View Site</a>
            <span class="user-info">Logged in as: admin</span>
            <a href="/admin/logout.php">Logout</a>
        </nav>
    </div>
    <div class="layout">
        <div class="sidebar">
            <h3>Content</h3>
            <ul>
                <li><a href="/admin/">Dashboard</a></li>
                <li><a href="/admin/pages.php">Pages</a></li>
                <li><a href="/admin/shared.php">Shared</a></li>
            </ul>
            <h3>Media</h3>
            <ul>
                <li><a href="/admin/images.php" class="active">Images</a></li>
                <li><a href="/admin/files.php">Files</a></li>
            </ul>
            <h3>System</h3>
            <ul>
                <li><a href="/admin/settings.php">Settings</a></li>
                <li><a href="/admin/users.php">Users</a></li>
                <li><a href="/admin/update.php">Update</a></li>
            </ul>
        </div>
        <div class="main">
            <div class="card">
                <h2>Upload Image</h2>
                <?php if ($message): ?>
                <div class="message <?php echo $message_type; ?>"><?php echo $message; ?></div>
                <?php endif; ?>
                
                <div class="dropzone" id="dropzone">
                    <p>Drop an image here or click to select</p>
                    <input type="file" id="fileInput" accept="image/*" style="display: none;">
                </div>
                <div class="preview" id="preview" style="display: none;">
                    <img id="previewImg" src="" alt="Preview">
                </div>
                
                <form method="POST" action="" id="uploadForm">
                    <input type="hidden" name="action" value="save">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="name">File Name</label>
                            <input type="text" id="name" name="name" placeholder="image-name" required>
                            <small>Alphanumeric characters, hyphens, and underscores only</small>
                        </div>
                        <div class="form-group">
                            <label for="extension">Extension</label>
                            <input type="text" id="extension" name="extension" placeholder="jpg" required>
                            <small>Allowed: <?php echo implode(', ', $allowed_types); ?></small>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="imageBase64">Image Data (Base64)</label>
                        <textarea id="imageBase64" name="imageBase64" placeholder="Paste base64-encoded image data or use the dropzone above"></textarea>
                    </div>
                    <button type="submit" class="btn">Save Image</button>
                </form>
            </div>
            
            <div class="card">
                <h2>Uploaded Images</h2>
                <?php if (empty($images)): ?>
                <p style="color: #666;">No images uploaded yet.</p>
                <?php else: ?>
                <div class="image-grid">
                    <?php foreach ($images as $img): ?>
                    <div class="image-item">
                        <a href="/uploads/<?php echo htmlspecialchars($img); ?>" target="_blank">
                            <img src="/uploads/<?php echo htmlspecialchars($img); ?>" alt="<?php echo htmlspecialchars($img); ?>" onerror="this.style.display='none'">
                        </a>
                        <p><a href="/uploads/<?php echo htmlspecialchars($img); ?>" target="_blank"><?php echo htmlspecialchars($img); ?></a></p>
                    </div>
                    <?php endforeach; ?>
                </div>
                <?php endif; ?>
            </div>
        </div>
    </div>
    
    <script>
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('fileInput');
        const preview = document.getElementById('preview');
        const previewImg = document.getElementById('previewImg');
        const nameInput = document.getElementById('name');
        const extensionInput = document.getElementById('extension');
        const base64Input = document.getElementById('imageBase64');
        
        dropzone.addEventListener('click', () => fileInput.click());
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
        dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            handleFile(e.dataTransfer.files[0]);
        });
        fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
        
        function handleFile(file) {
            if (!file) return;
            
            const nameParts = file.name.split('.');
            const ext = nameParts.pop();
            const name = nameParts.join('.').replace(/[^a-zA-Z0-9_-]/g, '-');
            
            nameInput.value = name || 'image';
            extensionInput.value = ext || '';
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const base64 = e.target.result.split(',')[1];
                base64Input.value = base64;
                previewImg.src = e.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    </script>
</body>
</html>
