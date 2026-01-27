<?php
/**
 * phpMyFAQ - Category Management
 * Admin panel for managing FAQ categories
 */

include("../include/db_config.php");

session_start();

$username = '';
if (isset($_SESSION['username'])){
    $username = $_SESSION['username'];
}

if(!$username){
    header("Location: ../index.php?error=failed_login");
    exit();
}

// Get categories from database
$categories = array();
$result = mysqli_query($db_connect, "SELECT * FROM faq_categories ORDER BY category_id");
while($row = mysqli_fetch_assoc($result)) {
    $categories[] = $row;
}

?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>phpMyFAQ Admin - Category Management</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="generator" content="phpMyFAQ 3.2.5">
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    
    <style>
        body { background: #f8f9fa; }
        .sidebar { background: #2c3e50; min-height: 100vh; }
        .sidebar a { color: #ecf0f1; display: block; padding: 12px 20px; text-decoration: none; }
        .sidebar a:hover { background: #34495e; }
        .sidebar a.active { background: #3498db; }
        .main-header { background: white; padding: 15px 20px; border-bottom: 1px solid #ddd; }
        .category-card { transition: transform 0.2s; }
        .category-card:hover { transform: translateY(-2px); }
        .category-img { width: 60px; height: 60px; object-fit: cover; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2 sidebar p-0">
                <div class="p-3 text-white">
                    <h5><i class="fas fa-question-circle"></i> phpMyFAQ</h5>
                    <small>Admin Panel v3.2.5</small>
                </div>
                <nav>
                    <a href="#"><i class="fas fa-tachometer-alt me-2"></i> Dashboard</a>
                    <a href="#" class="active"><i class="fas fa-folder me-2"></i> Categories</a>
                    <a href="#"><i class="fas fa-file-alt me-2"></i> FAQs</a>
                    <a href="#"><i class="fas fa-users me-2"></i> Users</a>
                    <a href="#"><i class="fas fa-cog me-2"></i> Settings</a>
                    <a href="logout.php"><i class="fas fa-sign-out-alt me-2"></i> Logout</a>
                </nav>
            </div>
            
            <!-- Main Content -->
            <div class="col-md-10 p-0">
                <div class="main-header d-flex justify-content-between align-items-center">
                    <h4 class="mb-0"><i class="fas fa-folder-open"></i> Category Management</h4>
                    <span class="text-muted">Logged in as: <strong><?php echo htmlspecialchars($username); ?></strong></span>
                </div>
                
                <div class="p-4">
                    <!-- Add New Category -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-plus-circle"></i> Add New Category</h5>
                        </div>
                        <div class="card-body">
                            <form id="categoryForm" action="category.upload.php" method="post" enctype="multipart/form-data">
                                <div class="row">
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">Category Name</label>
                                            <input type="text" name="category_name" class="form-control" required>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="mb-3">
                                            <label class="form-label">Language</label>
                                            <select name="lang" class="form-select" required>
                                                <option value="en">English (en)</option>
                                                <option value="de">German (de)</option>
                                                <option value="fr">French (fr)</option>
                                                <option value="es">Spanish (es)</option>
                                            </select>
                                            <!-- Category language determines image naming convention -->
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="mb-3">
                                            <label class="form-label">Category Image</label>
                                            <input type="file" name="image" class="form-control" accept="image/*">
                                            <small class="text-muted">Supported: PNG, JPG, GIF</small>
                                        </div>
                                    </div>
                                    <div class="col-md-2 d-flex align-items-end">
                                        <div class="mb-3">
                                            <button type="submit" class="btn btn-primary">
                                                <i class="fas fa-save"></i> Save Category
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                    
                    <!-- Upload Response -->
                    <div id="uploadResponse" class="mb-4"></div>
                    
                    <!-- Existing Categories -->
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-list"></i> Existing Categories</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Image</th>
                                            <th>Name</th>
                                            <th>Language</th>
                                            <th>Created</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php if(count($categories) > 0): ?>
                                            <?php foreach($categories as $cat): ?>
                                            <tr>
                                                <td><?php echo $cat['category_id']; ?></td>
                                                <td>
                                                    <?php if($cat['image_path']): ?>
                                                        <img src="../<?php echo htmlspecialchars($cat['image_path']); ?>" class="category-img" alt="Category Image">
                                                    <?php else: ?>
                                                        <span class="text-muted">No image</span>
                                                    <?php endif; ?>
                                                </td>
                                                <td><?php echo htmlspecialchars($cat['name']); ?></td>
                                                <td><?php echo htmlspecialchars($cat['lang']); ?></td>
                                                <td><?php echo $cat['created_at']; ?></td>
                                                <td>
                                                    <button class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i></button>
                                                    <button class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button>
                                                </td>
                                            </tr>
                                            <?php endforeach; ?>
                                        <?php else: ?>
                                            <tr>
                                                <td colspan="6" class="text-center text-muted">No categories found. Add your first category above.</td>
                                            </tr>
                                        <?php endif; ?>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Check for upload result in URL
        const urlParams = new URLSearchParams(window.location.search);
        if(urlParams.has('status')) {
            const status = urlParams.get('status');
            const msg = urlParams.get('msg') || '';
            const responseDiv = document.getElementById('uploadResponse');
            if(status === 'success') {
                responseDiv.innerHTML = '<div class="alert alert-success"><i class="fas fa-check-circle"></i> ' + decodeURIComponent(msg) + '</div>';
            } else {
                responseDiv.innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> ' + decodeURIComponent(msg) + '</div>';
            }
        }
    </script>
</body>
</html>
