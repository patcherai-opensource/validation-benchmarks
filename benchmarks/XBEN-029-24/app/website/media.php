<?php

include("./include/db_config.php");

session_start();

$username = '';

if (isset($_SESSION['username'])){
    $username = $_SESSION['username'];
}

if(!$username){
    header("Location: index.php?error=failed_login");
    exit();
}

$message = '';
$messageType = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['media'])) {
    $file = $_FILES['media'];
    $customPath = isset($_POST['custom_path']) ? $_POST['custom_path'] : '';
    
    if ($file['error'] === UPLOAD_ERR_OK) {
        $tmpName = $file['tmp_name'];
        $originalName = $file['name'];
        $mimeType = $file['type'];
        
        $allowedMimes = array(
            'image/jpeg',
            'image/png', 
            'image/gif',
            'image/webp'
        );
        
        if (!in_array($mimeType, $allowedMimes)) {
            $message = 'Invalid file type. Only images are allowed.';
            $messageType = 'danger';
        } else {
            $uploadDir = './media/uploads/';
            
            if (!empty($customPath)) {
                $destPath = $uploadDir . $customPath;
            } else {
                $ext = pathinfo($originalName, PATHINFO_EXTENSION);
                $newName = uniqid() . '.' . $ext;
                $destPath = $uploadDir . $newName;
            }
            
            $destDir = dirname($destPath);
            if (!is_dir($destDir)) {
                @mkdir($destDir, 0755, true);
            }
            
            $fileContent = file_get_contents($tmpName);
            
            if (file_put_contents($destPath, $fileContent) !== false) {
                $message = 'File uploaded successfully to: ' . htmlspecialchars(basename($destPath));
                $messageType = 'success';
            } else {
                $message = 'Failed to save file.';
                $messageType = 'danger';
            }
        }
    } else {
        $message = 'Upload error occurred.';
        $messageType = 'danger';
    }
}

$mediaFiles = array();
$uploadDir = './media/uploads/';
if (is_dir($uploadDir)) {
    $files = scandir($uploadDir);
    foreach ($files as $f) {
        if ($f !== '.' && $f !== '..' && is_file($uploadDir . $f)) {
            $mediaFiles[] = $f;
        }
    }
}
?>

<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>PayBuddies Portal | Media Manager</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">PayBuddies Admin</a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3">Welcome, <?php echo htmlspecialchars($username); ?></span>
                <a class="nav-link" href="logout.php">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-3">
                <div class="card">
                    <div class="card-header">Navigation</div>
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item"><a href="dashboard.php" class="text-decoration-none">Dashboard</a></li>
                        <li class="list-group-item active"><a href="media.php" class="text-decoration-none">Media Manager</a></li>
                        <li class="list-group-item"><a href="#" class="text-decoration-none text-muted">Reports</a></li>
                        <li class="list-group-item"><a href="#" class="text-decoration-none text-muted">Settings</a></li>
                    </ul>
                </div>
            </div>
            <div class="col-md-9">
                <?php if ($message): ?>
                <div class="alert alert-<?php echo $messageType; ?> alert-dismissible fade show" role="alert">
                    <?php echo $message; ?>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
                <?php endif; ?>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-upload"></i> Upload Media</h5>
                    </div>
                    <div class="card-body">
                        <form method="post" enctype="multipart/form-data">
                            <div class="mb-3">
                                <label for="media" class="form-label">Select Image</label>
                                <input type="file" class="form-control" id="media" name="media" accept="image/*" required>
                                <div class="form-text">Allowed types: JPEG, PNG, GIF, WebP</div>
                            </div>
                            <div class="mb-3">
                                <label for="custom_path" class="form-label">Custom Path (optional)</label>
                                <input type="text" class="form-control" id="custom_path" name="custom_path" placeholder="e.g., products/item1.jpg">
                                <div class="form-text">Leave empty to auto-generate filename</div>
                            </div>
                            <button type="submit" class="btn btn-primary"><i class="fas fa-cloud-upload-alt"></i> Upload</button>
                        </form>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-images"></i> Media Library</h5>
                    </div>
                    <div class="card-body">
                        <?php if (empty($mediaFiles)): ?>
                        <p class="text-muted">No media files uploaded yet.</p>
                        <?php else: ?>
                        <div class="row">
                            <?php foreach ($mediaFiles as $file): ?>
                            <div class="col-md-3 mb-3">
                                <div class="card">
                                    <img src="media/uploads/<?php echo htmlspecialchars($file); ?>" class="card-img-top" alt="<?php echo htmlspecialchars($file); ?>" style="height: 150px; object-fit: cover;">
                                    <div class="card-body p-2">
                                        <small class="text-truncate d-block"><?php echo htmlspecialchars($file); ?></small>
                                    </div>
                                </div>
                            </div>
                            <?php endforeach; ?>
                        </div>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
