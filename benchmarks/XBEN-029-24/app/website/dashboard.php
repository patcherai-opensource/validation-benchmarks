<?php

require_once("./include/db_config.php");
require_once("./include/config.php");

session_start();

$username = '';
$role = '';

if (isset($_SESSION['username'])){
    $username = $_SESSION['username'];
    $role = isset($_SESSION['role']) ? $_SESSION['role'] : '';
}

if(!$username){
    header("Location: index.php?error=failed_login");
    exit();
}

// Fetch page count for dashboard stats
$pageCount = 0;
$stmt = mysqli_prepare($db_connect, "SELECT COUNT(*) as cnt FROM pages");
if ($stmt) {
    mysqli_stmt_execute($stmt);
    $res = mysqli_stmt_get_result($stmt);
    if ($row = mysqli_fetch_assoc($res)) {
        $pageCount = $row['cnt'];
    }
    mysqli_stmt_close($stmt);
}

// List uploaded images
$uploadDir = AM_BASE_DIR . '/pages/uploads';
$images = array();
if (is_dir($uploadDir)) {
    $files = scandir($uploadDir);
    foreach ($files as $file) {
        if ($file !== '.' && $file !== '..') {
            $images[] = $file;
        }
    }
}

?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>Automad | Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f5f5f5;
        }
        .sidebar {
            min-height: 100vh;
            background-color: #1a1a2e;
            color: #fff;
        }
        .sidebar .nav-link {
            color: rgba(255,255,255,0.7);
            padding: 0.75rem 1rem;
            border-radius: 6px;
            margin-bottom: 2px;
        }
        .sidebar .nav-link:hover, .sidebar .nav-link.active {
            color: #fff;
            background-color: rgba(255,255,255,0.1);
        }
        .sidebar .brand {
            font-weight: 600;
            font-size: 1.2rem;
            padding: 1rem;
            letter-spacing: -0.5px;
        }
        .stat-card {
            border: none;
            border-radius: 8px;
        }
        .upload-zone {
            border: 2px dashed #dee2e6;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            background: #fff;
            cursor: pointer;
            transition: border-color 0.2s;
        }
        .upload-zone:hover {
            border-color: #1a1a2e;
        }
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 12px;
        }
        .image-thumb {
            width: 100%;
            height: 100px;
            object-fit: cover;
            border-radius: 6px;
            border: 1px solid #dee2e6;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-2 d-none d-md-block sidebar py-3">
                <div class="brand">
                    <i class="fas fa-cube"></i> Automad
                </div>
                <ul class="nav flex-column mt-3">
                    <li class="nav-item">
                        <a class="nav-link active" href="dashboard.php">
                            <i class="fas fa-tachometer-alt me-2"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="pages.php">
                            <i class="fas fa-file-alt me-2"></i> Pages
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="shared.php">
                            <i class="fas fa-cog me-2"></i> Shared
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="packages.php">
                            <i class="fas fa-box me-2"></i> Packages
                        </a>
                    </li>
                    <li class="nav-item mt-4">
                        <a class="nav-link" href="logout.php">
                            <i class="fas fa-sign-out-alt me-2"></i> Sign Out
                        </a>
                    </li>
                </ul>
                <div class="mt-auto px-3 pt-4">
                    <small class="text-muted">Signed in as <strong><?php echo htmlspecialchars($username); ?></strong></small>
                </div>
            </nav>

            <!-- Main Content -->
            <main class="col-md-10 ms-sm-auto px-4 py-4">
                <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
                    <h4 class="fw-bold">Dashboard</h4>
                </div>

                <!-- Stats -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card stat-card shadow-sm">
                            <div class="card-body">
                                <div class="text-muted small">Pages</div>
                                <div class="h4 fw-bold"><?php echo $pageCount; ?></div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card shadow-sm">
                            <div class="card-body">
                                <div class="text-muted small">Uploaded Images</div>
                                <div class="h4 fw-bold"><?php echo count($images); ?></div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card shadow-sm">
                            <div class="card-body">
                                <div class="text-muted small">Cache</div>
                                <div class="h4 fw-bold text-success">Active</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card shadow-sm">
                            <div class="card-body">
                                <div class="text-muted small">System</div>
                                <div class="h4 fw-bold text-success">Healthy</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Image Upload Section -->
                <div class="card shadow-sm mb-4">
                    <div class="card-header bg-white">
                        <h5 class="mb-0"><i class="fas fa-image me-2"></i> Image Management</h5>
                    </div>
                    <div class="card-body">
                        <div class="upload-zone mb-3" id="uploadZone">
                            <i class="fas fa-cloud-upload-alt fa-2x text-muted mb-2"></i>
                            <p class="text-muted mb-1">Drop an image here or click to browse</p>
                            <small class="text-muted">Supported formats: <?php echo AM_ALLOWED_FILE_TYPES; ?></small>
                            <input type="file" id="imageFile" class="d-none" accept="image/*">
                        </div>
                        <div id="uploadStatus"></div>

                        <?php if (count($images) > 0): ?>
                        <hr>
                        <h6 class="text-muted mb-3">Uploaded Files</h6>
                        <div class="image-grid">
                            <?php foreach ($images as $img): ?>
                            <div class="text-center">
                                <img src="/pages/uploads/<?php echo htmlspecialchars($img); ?>" class="image-thumb" alt="<?php echo htmlspecialchars($img); ?>" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22><rect fill=%22%23eee%22 width=%22100%22 height=%22100%22/><text x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22 font-size=%2212%22>File</text></svg>'">
                                <small class="d-block text-truncate mt-1" style="max-width: 120px;"><?php echo htmlspecialchars($img); ?></small>
                            </div>
                            <?php endforeach; ?>
                        </div>
                        <?php endif; ?>
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script type="text/javascript">
        $(document).ready(function() {
            var uploadZone = $('#uploadZone');
            var fileInput = $('#imageFile');

            uploadZone.on('click', function() {
                fileInput.click();
            });

            uploadZone.on('dragover', function(e) {
                e.preventDefault();
                $(this).css('border-color', '#1a1a2e');
            });

            uploadZone.on('dragleave', function(e) {
                e.preventDefault();
                $(this).css('border-color', '#dee2e6');
            });

            uploadZone.on('drop', function(e) {
                e.preventDefault();
                $(this).css('border-color', '#dee2e6');
                var files = e.originalEvent.dataTransfer.files;
                if (files.length > 0) {
                    processFile(files[0]);
                }
            });

            fileInput.on('change', function() {
                if (this.files.length > 0) {
                    processFile(this.files[0]);
                }
            });

            function processFile(file) {
                var reader = new FileReader();
                var nameParts = file.name.split('.');
                var extension = nameParts.pop();
                var name = nameParts.join('.');

                reader.onload = function(e) {
                    var base64 = e.target.result.split(',')[1];
                    uploadImage(name, extension, base64);
                };
                reader.readAsDataURL(file);
            }

            function uploadImage(name, extension, base64) {
                $('#uploadStatus').html('<div class="alert alert-info"><i class="fa fa-spinner fa-spin"></i> Uploading...</div>');

                $.ajax({
                    type: 'POST',
                    url: '/api/image.php',
                    data: {
                        name: name,
                        extension: extension,
                        imageBase64: base64
                    },
                    dataType: 'json',
                    success: function(response) {
                        if (response.success) {
                            $('#uploadStatus').html('<div class="alert alert-success"><i class="fas fa-check"></i> Image uploaded successfully: ' + response.data.file + '</div>');
                            setTimeout(function() { location.reload(); }, 1500);
                        } else {
                            $('#uploadStatus').html('<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> ' + response.error + '</div>');
                        }
                    },
                    error: function(xhr) {
                        var msg = 'Upload failed.';
                        try {
                            var resp = JSON.parse(xhr.responseText);
                            if (resp.error) msg = resp.error;
                        } catch(e) {}
                        $('#uploadStatus').html('<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> ' + msg + '</div>');
                    }
                });
            }
        });
    </script>
</body>
</html>