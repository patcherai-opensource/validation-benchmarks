<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

require_once(__DIR__ . '/../include/db_config.php');
require_once(__DIR__ . '/../include/auth.php');
require_once(__DIR__ . '/../include/config.php');

requireAuth();

$username = $_SESSION['username'];
$role = $_SESSION['role'];
$csrfToken = getCsrfToken();
$allowedTypes = getAllowedFileTypes();

$mediaFiles = array();
$result = mysqli_query($db_connect, "SELECT mf.*, u.username as uploader FROM media_files mf LEFT JOIN users u ON mf.uploaded_by = u.id ORDER BY mf.created_at DESC LIMIT 50");
if ($result) {
    while ($row = mysqli_fetch_assoc($result)) {
        $mediaFiles[] = $row;
    }
}

?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf" content="<?php echo $csrfToken; ?>">
    <meta name="robots" content="noindex">
    <title>SiteCraft CMS | Media Library</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .sidebar { min-height: 100vh; background: #1e293b; padding-top: 20px; }
        .sidebar .nav-link { color: #94a3b8; padding: 12px 20px; }
        .sidebar .nav-link:hover, .sidebar .nav-link.active { color: #fff; background: rgba(255,255,255,0.1); }
        .sidebar .brand { color: #fff; font-size: 20px; font-weight: bold; padding: 0 20px 20px; border-bottom: 1px solid #334155; margin-bottom: 10px; }
        .content-area { padding: 30px; }
        .card { border: none; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .media-thumb { width: 60px; height: 60px; object-fit: cover; border-radius: 8px; background: #e2e8f0; display: flex; align-items: center; justify-content: center; color: #64748b; }
        .drop-zone { border: 2px dashed #cbd5e1; border-radius: 12px; padding: 40px; text-align: center; cursor: pointer; transition: all 0.2s; }
        .drop-zone:hover, .drop-zone.active { border-color: #1a73e8; background: #eff6ff; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 sidebar d-none d-md-block">
                <div class="brand"><i class="fas fa-cube"></i> SiteCraft</div>
                <ul class="nav flex-column">
                    <li class="nav-item"><a class="nav-link" href="/admin/dashboard.php"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="/admin/pages.php"><i class="fas fa-file-alt me-2"></i>Pages</a></li>
                    <li class="nav-item"><a class="nav-link active" href="/admin/media.php"><i class="fas fa-images me-2"></i>Media</a></li>
                    <?php if ($role === 'admin'): ?>
                    <li class="nav-item"><a class="nav-link" href="/admin/settings.php"><i class="fas fa-cog me-2"></i>Settings</a></li>
                    <?php endif; ?>
                    <li class="nav-item mt-4"><a class="nav-link" href="/admin/logout.php"><i class="fas fa-sign-out-alt me-2"></i>Sign Out</a></li>
                </ul>
            </nav>
            <main class="col-md-10 ms-sm-auto content-area">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h3>Media Library</h3>
                    <span class="badge bg-primary"><?php echo htmlspecialchars($role); ?>: <?php echo htmlspecialchars($username); ?></span>
                </div>

                <div class="card mb-4">
                    <div class="card-body">
                        <h5 class="card-title">Upload Media</h5>
                        <p class="text-muted">Drag and drop files or use the editor below. Accepted types: <code><?php echo htmlspecialchars(implode(', ', $allowedTypes)); ?></code></p>
                        <div class="drop-zone" id="dropZone">
                            <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                            <p class="mb-2">Drop files here or click to browse</p>
                            <input type="file" id="fileInput" class="d-none" multiple>
                        </div>
                        <div id="uploadStatus" class="mt-3"></div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Files</h5>
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th></th>
                                        <th>Filename</th>
                                        <th>Type</th>
                                        <th>Size</th>
                                        <th>Uploaded By</th>
                                        <th>Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php if (empty($mediaFiles)): ?>
                                    <tr><td colspan="6" class="text-center text-muted">No media files uploaded yet</td></tr>
                                    <?php else: ?>
                                    <?php foreach ($mediaFiles as $file): ?>
                                    <tr>
                                        <td><div class="media-thumb"><i class="fas fa-file"></i></div></td>
                                        <td><?php echo htmlspecialchars($file['filename']); ?></td>
                                        <td><span class="badge bg-secondary"><?php echo htmlspecialchars($file['file_type']); ?></span></td>
                                        <td><?php echo number_format($file['file_size'] / 1024, 1); ?> KB</td>
                                        <td><?php echo htmlspecialchars($file['uploader'] ?? 'Unknown'); ?></td>
                                        <td><?php echo $file['created_at']; ?></td>
                                    </tr>
                                    <?php endforeach; ?>
                                    <?php endif; ?>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        $(document).ready(function() {
            var csrfToken = $('meta[name="csrf"]').attr('content');
            var dropZone = $('#dropZone');
            var fileInput = $('#fileInput');

            dropZone.on('click', function() { fileInput.click(); });
            dropZone.on('dragover', function(e) { e.preventDefault(); $(this).addClass('active'); });
            dropZone.on('dragleave', function() { $(this).removeClass('active'); });
            dropZone.on('drop', function(e) {
                e.preventDefault();
                $(this).removeClass('active');
                handleFiles(e.originalEvent.dataTransfer.files);
            });
            fileInput.on('change', function() { handleFiles(this.files); });

            function handleFiles(files) {
                Array.from(files).forEach(function(file) {
                    var reader = new FileReader();
                    reader.onload = function(e) {
                        var base64Data = e.target.result;
                        var nameParts = file.name.split('.');
                        var ext = nameParts.pop();
                        var name = nameParts.join('.');

                        $.ajax({
                            type: 'POST',
                            url: '/api/media/store.php',
                            contentType: 'application/json',
                            data: JSON.stringify({
                                name: name,
                                extension: ext,
                                fileData: base64Data,
                                __csrf__: csrfToken
                            }),
                            success: function(resp) {
                                if (resp.error) {
                                    $('#uploadStatus').html('<div class="alert alert-danger">' + resp.error + '</div>');
                                } else {
                                    $('#uploadStatus').html('<div class="alert alert-success">File uploaded: ' + resp.filename + '</div>');
                                    setTimeout(function() { location.reload(); }, 1500);
                                }
                            },
                            error: function(xhr) {
                                var msg = 'Upload failed';
                                try { msg = JSON.parse(xhr.responseText).error || msg; } catch(e) {}
                                $('#uploadStatus').html('<div class="alert alert-danger">' + msg + '</div>');
                            }
                        });
                    };
                    reader.readAsDataURL(file);
                });
            }
        });
    </script>
</body>
</html>
