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

// Fetch categories from database
$categories = mysqli_query($db_connect, "SELECT * FROM categories ORDER BY name");

?>

<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>PayBuddies Portal | Admin Dashboard</title>
    <meta name="description" content="">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">PayBuddies Admin</a>
            <span class="navbar-text text-white">
                Welcome, <?php echo htmlspecialchars($username); ?> | <a href="logout.php" class="text-white">Logout</a>
            </span>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-12">
                <h2>Category Management</h2>
                <p class="lead">Manage document categories and upload category images.</p>
                
                <div class="card shadow-sm mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Upload Category Image</h5>
                    </div>
                    <div class="card-body">
                        <form id="categoryImageForm" method="post" action="upload.php" enctype="multipart/form-data">
                            <div class="row">
                                <div class="col-md-4 mb-3">
                                    <label for="category_id" class="form-label">Category</label>
                                    <select class="form-select" id="category_id" name="category_id" required>
                                        <?php while($cat = mysqli_fetch_assoc($categories)): ?>
                                            <option value="<?php echo $cat['category_id']; ?>"><?php echo htmlspecialchars($cat['name']); ?></option>
                                        <?php endwhile; ?>
                                    </select>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label for="lang" class="form-label">Language Code</label>
                                    <input type="text" class="form-control" id="lang" name="lang" value="en" placeholder="e.g., en, de, fr">
                                    <small class="text-muted">Language code for the category image</small>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label for="image" class="form-label">Category Image</label>
                                    <input type="file" class="form-control" id="image" name="image" accept="image/*" required>
                                    <small class="text-muted">Supported: PNG, JPG, GIF</small>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary"><i class="fas fa-upload"></i> Upload Image</button>
                        </form>
                    </div>
                </div>
                
                <div class="card shadow-sm">
                    <div class="card-header">
                        <h5 class="mb-0">Categories</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Language</th>
                                    <th>Image</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php 
                                mysqli_data_seek($categories, 0);
                                while($cat = mysqli_fetch_assoc($categories)): 
                                ?>
                                <tr>
                                    <td><?php echo $cat['category_id']; ?></td>
                                    <td><?php echo htmlspecialchars($cat['name']); ?></td>
                                    <td><?php echo htmlspecialchars($cat['lang']); ?></td>
                                    <td>
                                        <?php if($cat['image_path']): ?>
                                            <a href="<?php echo htmlspecialchars($cat['image_path']); ?>" target="_blank">View</a>
                                        <?php else: ?>
                                            <span class="text-muted">No image</span>
                                        <?php endif; ?>
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

    <!-- Bootstrap JS and dependencies -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
