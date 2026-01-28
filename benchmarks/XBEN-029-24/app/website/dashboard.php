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

// Get list of uploaded media files
$uploadDir = './media/products/';
$mediaFiles = array();
if (is_dir($uploadDir)) {
    $files = scandir($uploadDir);
    foreach ($files as $file) {
        if ($file !== '.' && $file !== '..') {
            $mediaFiles[] = $file;
        }
    }
}

?>

<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>Aimeos Media Manager | Dashboard</title>
    <meta name="description" content="Aimeos e-commerce media management">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <style>
        .aimeos-brand { font-weight: bold; color: #0066cc; }
        .nav-link.active { background-color: #0066cc !important; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand aimeos-brand text-white" href="#"><i class="fas fa-images"></i> Aimeos Media Manager</a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text text-white me-3">
                    <i class="fas fa-user"></i> <?php echo htmlspecialchars($username); ?>
                </span>
                <a class="nav-link text-white" href="logout.php"><i class="fas fa-sign-out-alt"></i> Logout</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-3">
                <div class="card">
                    <div class="card-header bg-secondary text-white">
                        <i class="fas fa-bars"></i> Navigation
                    </div>
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item"><a href="dashboard.php" class="text-decoration-none"><i class="fas fa-tachometer-alt"></i> Dashboard</a></li>
                        <li class="list-group-item"><a href="products.php" class="text-decoration-none"><i class="fas fa-box"></i> Products</a></li>
                        <li class="list-group-item active bg-primary"><a href="#" class="text-decoration-none text-white"><i class="fas fa-upload"></i> Media Upload</a></li>
                        <li class="list-group-item"><a href="settings.php" class="text-decoration-none"><i class="fas fa-cog"></i> Settings</a></li>
                        <li class="list-group-item"><a href="api-docs.php" class="text-decoration-none"><i class="fas fa-book"></i> API Docs</a></li>
                    </ul>
                </div>
            </div>
            <div class="col-md-9">
                <div class="card shadow-sm">
                    <div class="card-header bg-primary text-white">
                        <i class="fas fa-cloud-upload-alt"></i> Upload Product Media
                    </div>
                    <div class="card-body">
                        <p class="text-muted">Upload product images for your e-commerce catalog. Supported formats: JPEG, PNG, GIF, WebP.</p>
                        <form id="uploadForm" method="post" action="upload.php" enctype="multipart/form-data">
                            <div class="mb-3">
                                <label for="media" class="form-label">Select Image File</label>
                                <input type="file" class="form-control" id="media" name="media" accept="image/*" required>
                                <small class="form-text text-muted">Max file size: 10MB. Allowed types: image/jpeg, image/png, image/gif, image/webp</small>
                            </div>
                            <div class="mb-3">
                                <label for="domain" class="form-label">Product Domain</label>
                                <select class="form-select" id="domain" name="domain">
                                    <option value="product">Products</option>
                                    <option value="catalog">Catalog</option>
                                    <option value="supplier">Suppliers</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-primary"><i class="fas fa-upload"></i> Upload Media</button>
                        </form>
                        <div class="uploadResponse mt-3"></div>
                    </div>
                </div>
                
                <div class="card shadow-sm mt-4">
                    <div class="card-header bg-secondary text-white">
                        <i class="fas fa-folder-open"></i> Recent Media Files
                    </div>
                    <div class="card-body">
                        <?php if (count($mediaFiles) > 0): ?>
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Filename</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php foreach ($mediaFiles as $file): ?>
                                        <tr>
                                            <td><?php echo htmlspecialchars($file); ?></td>
                                            <td><a href="media/products/<?php echo htmlspecialchars($file); ?>" class="btn btn-sm btn-outline-primary" target="_blank"><i class="fas fa-eye"></i> View</a></td>
                                        </tr>
                                        <?php endforeach; ?>
                                    </tbody>
                                </table>
                            </div>
                        <?php else: ?>
                            <p class="text-muted">No media files uploaded yet.</p>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-light text-center text-muted py-3 mt-4">
        <small>&copy; 2024 Aimeos Ltd. | Media Manager v2024.1.3</small>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script type="text/javascript">
        $(document).ready(function() {
            $("#uploadForm").submit(function(event) {
                event.preventDefault();
                
                var formData = new FormData(this);
                $(".uploadResponse").html('<div class="alert alert-info"><i class="fa fa-spinner fa-spin"></i> Uploading...</div>');
                
                $.ajax({
                    type: 'POST',
                    url: 'upload.php',
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function(response) {
                        if (response.includes('successfully')) {
                            $(".uploadResponse").html('<div class="alert alert-success">' + response + '</div>');
                            setTimeout(function() { location.reload(); }, 2000);
                        } else {
                            $(".uploadResponse").html('<div class="alert alert-danger">' + response + '</div>');
                        }
                    },
                    error: function() {
                        $(".uploadResponse").html('<div class="alert alert-danger">Upload failed. Please try again.</div>');
                    }
                });
            });
        });
    </script>
</body>
</html>
