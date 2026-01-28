<?php
/**
 * phpDocFAQ Category Management
 * Version 3.2.5
 */

include("../include/db_config.php");
session_start();

if (!isset($_SESSION['username'])) {
    header("Location: /index.php?error=failed_login");
    exit();
}

$username = $_SESSION['username'];

// Fetch categories from database
$categories_query = "SELECT * FROM categories ORDER BY category_id";
$categories_result = mysqli_query($db_connect, $categories_query);
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>phpDocFAQ - Category Management</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="/admin/dashboard.php">
                <i class="fas fa-question-circle"></i> phpDocFAQ Admin
            </a>
            <div class="navbar-nav ms-auto">
                <span class="nav-item nav-link text-white">
                    <i class="fas fa-user"></i> <?php echo htmlspecialchars($username); ?>
                </span>
                <a class="nav-link text-white" href="/admin/logout.php">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-md-3">
                <div class="card">
                    <div class="card-header bg-secondary text-white">
                        <i class="fas fa-cogs"></i> Administration
                    </div>
                    <div class="list-group list-group-flush">
                        <a href="/admin/dashboard.php" class="list-group-item list-group-item-action">
                            <i class="fas fa-tachometer-alt"></i> Dashboard
                        </a>
                        <a href="/admin/categories.php" class="list-group-item list-group-item-action active">
                            <i class="fas fa-folder"></i> Categories
                        </a>
                        <a href="/admin/faqs.php" class="list-group-item list-group-item-action">
                            <i class="fas fa-question"></i> FAQ Management
                        </a>
                        <a href="/admin/users.php" class="list-group-item list-group-item-action">
                            <i class="fas fa-users"></i> User Management
                        </a>
                        <a href="/admin/settings.php" class="list-group-item list-group-item-action">
                            <i class="fas fa-sliders-h"></i> Settings
                        </a>
                        <a href="/admin/backup.php" class="list-group-item list-group-item-action">
                            <i class="fas fa-database"></i> Backup
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-9">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-folder"></i> Category Management</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i> 
                            Manage FAQ categories and upload custom category images
                        </div>
                        
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Language</th>
                                    <th>Image</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php while ($cat = mysqli_fetch_assoc($categories_result)): ?>
                                <tr>
                                    <td><?php echo $cat['category_id']; ?></td>
                                    <td><?php echo htmlspecialchars($cat['name']); ?></td>
                                    <td><?php echo htmlspecialchars($cat['lang']); ?></td>
                                    <td>
                                        <?php if (!empty($cat['image_path'])): ?>
                                            <img src="<?php echo htmlspecialchars($cat['image_path']); ?>" alt="Category image" style="max-width: 50px; max-height: 50px;">
                                        <?php else: ?>
                                            <span class="text-muted">No image</span>
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <button class="btn btn-sm btn-primary upload-btn" data-id="<?php echo $cat['category_id']; ?>" data-lang="<?php echo $cat['lang']; ?>">
                                            <i class="fas fa-upload"></i> Upload Image
                                        </button>
                                    </td>
                                </tr>
                                <?php endwhile; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Upload Modal -->
    <div class="modal fade" id="uploadModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Upload Category Image</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="uploadForm" enctype="multipart/form-data">
                        <input type="hidden" id="category_id" name="category_id">
                        <input type="hidden" id="lang" name="lang">
                        
                        <div class="mb-3">
                            <label class="form-label">Category ID: <span id="display_id"></span></label>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Language: <span id="display_lang"></span></label>
                        </div>
                        <div class="mb-3">
                            <label for="image" class="form-label">Image File</label>
                            <input type="file" class="form-control" id="image" name="image" accept="image/*" required>
                            <div class="form-text">Supported: GIF, JPEG, PNG, WebP</div>
                        </div>
                    </form>
                    <div id="uploadResult"></div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="uploadBtn">Upload</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        $(document).ready(function() {
            var uploadModal = new bootstrap.Modal($('#uploadModal')[0]);
            
            $('.upload-btn').click(function() {
                var categoryId = $(this).data('id');
                var lang = $(this).data('lang');
                
                $('#category_id').val(categoryId);
                $('#lang').val(lang);
                $('#display_id').text(categoryId);
                $('#display_lang').text(lang);
                $('#uploadResult').empty();
                
                uploadModal.show();
            });
            
            $('#uploadBtn').click(function() {
                var formData = new FormData($('#uploadForm')[0]);
                
                $.ajax({
                    url: '/admin/category-image.php',
                    type: 'POST',
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function(response) {
                        if (response.success) {
                            $('#uploadResult').html('<div class="alert alert-success">' + response.message + '</div>');
                            setTimeout(function() {
                                location.reload();
                            }, 1500);
                        } else {
                            $('#uploadResult').html('<div class="alert alert-danger">' + response.message + '</div>');
                        }
                    },
                    error: function() {
                        $('#uploadResult').html('<div class="alert alert-danger">Upload failed</div>');
                    }
                });
            });
        });
    </script>
</body>
</html>
