<?php
// Define variables and initialize with empty values
$title = $description = "";
$title_err = $description_err = $file_err = "";
$succ_message = "";
$uploaded_path = "";

// File extension blacklist for security
// Prevents upload of common script extensions
$blacklist = array('exe', 'sh', 'bat', 'cmd', 'com', 'js', 'vbs');

function getFileExtension($filename) {
    $parts = explode('.', $filename);
    if (count($parts) > 1) {
        return strtolower(end($parts));
    }
    return '';
}

// Processing form data when form is submitted
if($_SERVER["REQUEST_METHOD"] == "POST"){
    // Validate title
    if(empty(trim($_POST["title"]))){
        $title_err = "Please enter a content title.";
    } else{
        $title = trim($_POST["title"]);
    }
    
    // Validate description
    if(empty(trim($_POST["description"]))){
        $description_err = "Please enter a description.";
    } else{
        $description = trim($_POST["description"]);
    }

    // Handle file upload
    if(isset($_FILES["mediaFile"]) && $_FILES["mediaFile"]["error"] == 0){
        $target_dir = "uploads/";
        $filename = basename($_FILES["mediaFile"]["name"]);
        $ext = getFileExtension($filename);
        
        // Security check: block dangerous extensions
        if(in_array($ext, $blacklist)) {
            $file_err = "Error: File type '" . htmlspecialchars($ext) . "' is not allowed for security reasons.";
        } else {
            $target_file = $target_dir . $filename;
            if(move_uploaded_file($_FILES["mediaFile"]["tmp_name"], $target_file)){
                $uploaded_path = $target_file;
            } else {
                $file_err = "Error uploading file.";
            }
        }
    } else{
        $file_err = "Please upload a file.";
    }

    // Check input errors before showing message
    if(empty($title_err) && empty($description_err) && empty($file_err)){
        $succ_message = "<div class='alert alert-success'><h4>Content uploaded successfully!</h4><p>Your media has been stored at: <code>/posts/" . htmlspecialchars($uploaded_path) . "</code></p></div>";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>eZ Content Hub | Media Upload</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <? include("../include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Content Media Upload</h1>
                <p class="lead">Upload images, documents, and other media files</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="container mt-5">
                    <?php if (empty($succ_message)){ ?>
                    <div class="card">
                        <div class="card-header">
                            <h5>Upload New Media Content</h5>
                        </div>
                        <div class="card-body">
                            <p>Use this form to upload media files for your content. Supported formats include images (jpg, png, gif, webp), documents (pdf, doc, txt), and more.</p>
                            <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post" enctype="multipart/form-data">
                                <div class="mb-3">
                                    <label class="form-label">Content Title</label>
                                    <input type="text" name="title" class="form-control" value="<?php echo $title; ?>" placeholder="Enter a descriptive title">
                                    <span class="text-danger small"><?php echo $title_err; ?></span>
                                </div>    
                                <div class="mb-3">
                                    <label class="form-label">Description</label>
                                    <textarea name="description" class="form-control" rows="3" placeholder="Brief description of the content"><?php echo $description; ?></textarea>
                                    <span class="text-danger small"><?php echo $description_err; ?></span>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Media File (ezbinaryfile)</label>
                                    <input type="file" name="mediaFile" class="form-control">
                                    <span class="text-danger small"><?php echo $file_err; ?></span>
                                    <div class="form-text">Max file size: 10MB</div>
                                </div>
                                <div class="mb-3">
                                    <button type="submit" class="btn btn-primary">Upload Content</button>
                                </div>
                            </form>
                        </div>
                    </div>
                    <?php } else { echo $succ_message; }?>
                </div>
            </div>
        <!-- Sidebar Widgets Column -->
        <? include("../include/sidebar.php") ?>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
