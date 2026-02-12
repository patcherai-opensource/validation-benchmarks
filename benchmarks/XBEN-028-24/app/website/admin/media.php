<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$user = getCurrentUser();
$db = getDb();

$media = $db->query("SELECT * FROM mshop_media ORDER BY id DESC")->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aimeos CMS - Media Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background: #343a40; }
        .sidebar a { color: #adb5bd; text-decoration: none; padding: 10px 20px; display: block; }
        .sidebar a:hover, .sidebar a.active { color: white; background: #495057; }
        .content { padding: 20px; }
        .media-thumb { width: 60px; height: 60px; object-fit: cover; border-radius: 4px; background: #e9ecef; display: flex; align-items: center; justify-content: center; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 sidebar py-3">
                <h5 class="text-white px-3 mb-4">Aimeos CMS</h5>
                <a href="/admin/dashboard.php"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a>
                <a href="/admin/media.php" class="active"><i class="fas fa-images me-2"></i>Media</a>
                <a href="/admin/products.php"><i class="fas fa-box me-2"></i>Products</a>
                <hr class="text-secondary">
                <a href="/admin/logout.php"><i class="fas fa-sign-out-alt me-2"></i>Logout</a>
                <a href="/" class="mt-3"><i class="fas fa-arrow-left me-2"></i>Back to Blog</a>
            </nav>
            <main class="col-md-10 content">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2>Media Manager</h2>
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#uploadModal">
                        <i class="fas fa-upload me-1"></i> Upload Media
                    </button>
                </div>

                <div id="alertContainer"></div>

                <div class="card">
                    <div class="card-body">
                        <table class="table table-hover" id="mediaTable">
                            <thead>
                                <tr>
                                    <th width="80">Preview</th>
                                    <th>Label</th>
                                    <th>Domain</th>
                                    <th>Type</th>
                                    <th>MIME Type</th>
                                    <th>URL</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($media as $item): ?>
                                <tr data-id="<?= $item['id'] ?>">
                                    <td>
                                        <div class="media-thumb">
                                            <?php if (strpos($item['mimetype'], 'image/') === 0): ?>
                                                <img src="/<?= htmlspecialchars($item['url']) ?>" style="width:60px;height:60px;object-fit:cover;border-radius:4px;" onerror="this.parentElement.innerHTML='<i class=\'fas fa-image text-muted\'></i>'">
                                            <?php else: ?>
                                                <i class="fas fa-file text-muted"></i>
                                            <?php endif; ?>
                                        </div>
                                    </td>
                                    <td><?= htmlspecialchars($item['label']) ?></td>
                                    <td><?= htmlspecialchars($item['domain']) ?></td>
                                    <td><?= htmlspecialchars($item['type']) ?></td>
                                    <td><code><?= htmlspecialchars($item['mimetype']) ?></code></td>
                                    <td><code class="small"><?= htmlspecialchars($item['url']) ?></code></td>
                                    <td>
                                        <?php if ($item['status'] == 1): ?>
                                            <span class="badge bg-success">Active</span>
                                        <?php else: ?>
                                            <span class="badge bg-secondary">Inactive</span>
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <button class="btn btn-sm btn-outline-danger" onclick="deleteMedia(<?= $item['id'] ?>)">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        </div>
    </div>

    <!-- Upload Modal -->
    <div class="modal fade" id="uploadModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Upload Media</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="uploadForm" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label for="mediaLabel" class="form-label">Label <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="mediaLabel" name="media.label" required>
                        </div>
                        <div class="mb-3">
                            <label for="mediaDomain" class="form-label">Domain</label>
                            <select class="form-select" id="mediaDomain" name="media.domain">
                                <option value="product">Product</option>
                                <option value="catalog">Catalog</option>
                                <option value="supplier">Supplier</option>
                                <option value="cms">CMS</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="mediaType" class="form-label">Type</label>
                            <select class="form-select" id="mediaType" name="media.type">
                                <option value="default">Default</option>
                                <option value="icon">Icon</option>
                                <option value="stage">Stage</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="mediaUrl" class="form-label">URL Path</label>
                            <input type="text" class="form-control" id="mediaUrl" name="media.url" 
                                   placeholder="Leave empty for auto-generated path">
                            <div class="form-text">Optional: specify a custom storage path for the media file.</div>
                        </div>
                        <div class="mb-3">
                            <label for="mediaFile" class="form-label">File <span class="text-danger">*</span></label>
                            <input type="file" class="form-control" id="mediaFile" name="media.file" required>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="uploadMedia()">Upload</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function showAlert(message, type) {
            document.getElementById('alertContainer').innerHTML = 
                '<div class="alert alert-' + type + ' alert-dismissible fade show">' + 
                message + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>';
        }

        function uploadMedia() {
            var form = document.getElementById('uploadForm');
            var formData = new FormData(form);

            fetch('/admin/api/media.php', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Media uploaded successfully.', 'success');
                    bootstrap.Modal.getInstance(document.getElementById('uploadModal')).hide();
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showAlert(data.error || 'Upload failed.', 'danger');
                }
            })
            .catch(err => {
                showAlert('An error occurred during upload.', 'danger');
            });
        }

        function deleteMedia(id) {
            if (!confirm('Are you sure you want to delete this media item?')) return;

            fetch('/admin/api/media.php?id=' + id, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Media deleted.', 'success');
                    document.querySelector('tr[data-id="' + id + '"]').remove();
                } else {
                    showAlert(data.error || 'Delete failed.', 'danger');
                }
            });
        }
    </script>
</body>
</html>
