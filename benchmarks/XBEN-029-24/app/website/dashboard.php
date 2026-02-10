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

?>

<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>PayBuddies Admin | Media Manager</title>
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
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="text-center mt-5">
                    <h1>Media Manager</h1>
                    <p class="lead">Upload images for your product catalog</p>
                </div>
                <div class="card shadow-sm">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-images"></i> Upload Media</h5>
                    </div>
                    <div class="card-body">
                        <form id="uploadForm" method="post" action="upload.php" enctype="multipart/form-data">
                            <div class="mb-3">
                                <label for="media" class="form-label">Image File</label>
                                <input type="file" class="form-control" id="media" name="media" accept="image/*" required>
                                <small class="text-muted">Allowed formats: JPEG, PNG, GIF, SVG</small>
                                <div class="text-danger mediaerror mt-2"></div>
                            </div>
                            <div class="mb-3">
                                <label for="path" class="form-label">Custom Path (optional)</label>
                                <input type="text" class="form-control" id="path" name="path" placeholder="e.g., products/image.jpg">
                                <small class="text-muted">Leave empty for auto-generated path</small>
                            </div>
                            <button type="submit" class="btn btn-primary w-100"><i class="fas fa-upload"></i> Upload Media</button>
                        </form>
                    </div>
                </div>
                <div class="LogResponse mt-3"></div>
                
                <div class="card shadow-sm mt-4">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-info-circle"></i> Admin Information</h5>
                    </div>
                    <div class="card-body">
                        <p>Welcome, <strong><?php echo htmlspecialchars($username); ?></strong></p>
                        <p>You are logged in as an administrator. You can upload media files to the system.</p>
                        <p class="text-muted small">Uploaded files are stored in <code>/media/</code> directory.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS and dependencies -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script type="text/javascript">
        $(document).ready(function() {
            $("#uploadForm").submit(function(event) {
                var fileInput = $("#media");
                var filePath = fileInput.val();
                var allowedExtensions = /\.(jpg|jpeg|png|gif|svg)$/i;
                
                if (!allowedExtensions.exec(filePath)) {
                    event.preventDefault();
                    $(".mediaerror").html("Please upload a valid image file (JPG, PNG, GIF, or SVG).");
                    fileInput.val('');
                    return false;
                } else {
                    $(".mediaerror").empty();
                }
            });
        });
    </script>
</body>
</html>
