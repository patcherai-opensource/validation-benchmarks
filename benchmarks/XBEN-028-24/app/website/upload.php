<?php
// DocuVault CMS - File Upload Module
// Version 2.3.1

$upload_message = "";
$upload_status = "";

// Define allowed extensions - basic check only (VULNERABLE: incomplete blacklist)
$blocked_extensions = array('exe', 'bat', 'cmd', 'com', 'msi');

function get_file_extension($filename) {
    return strtolower(pathinfo($filename, PATHINFO_EXTENSION));
}

function is_extension_blocked($filename, $blocked_list) {
    $ext = get_file_extension($filename);
    return in_array($ext, $blocked_list);
}

// Processing form data when form is submitted
if($_SERVER["REQUEST_METHOD"] == "POST"){
    if(isset($_FILES["document"]) && $_FILES["document"]["error"] == 0){
        $original_name = basename($_FILES["document"]["name"]);
        
        // Check against blocked extensions
        if(is_extension_blocked($original_name, $blocked_extensions)) {
            $upload_message = "Error: Executable files (.exe, .bat, .cmd, .com, .msi) are not allowed for security reasons.";
            $upload_status = "danger";
        } else {
            // Create uploads directory if it doesn't exist
            $target_dir = "files/";
            if (!file_exists($target_dir)) {
                mkdir($target_dir, 0755, true);
            }
            
            $target_file = $target_dir . $original_name;
            
            // Check file size (max 10MB)
            if ($_FILES["document"]["size"] > 10485760) {
                $upload_message = "Error: File size exceeds maximum limit of 10MB.";
                $upload_status = "danger";
            } else {
                if (move_uploaded_file($_FILES["document"]["tmp_name"], $target_file)) {
                    $upload_message = "File <strong>" . htmlspecialchars($original_name) . "</strong> has been uploaded successfully.";
                    $upload_message .= "<br><small>Access your file at: <a href='/files/" . htmlspecialchars($original_name) . "'>/files/" . htmlspecialchars($original_name) . "</a></small>";
                    $upload_status = "success";
                } else {
                    $upload_message = "Error: There was an error uploading your file.";
                    $upload_status = "danger";
                }
            }
        }
    } else {
        $upload_message = "Please select a file to upload.";
        $upload_status = "warning";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DocuVault CMS | File Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-4 bg-primary text-white mb-4">
        <div class="container">
            <div class="text-center my-3">
                <h1 class="fw-bolder"><i class="bi bi-cloud-upload"></i> File Manager</h1>
                <p class="lead mb-0">Upload and manage your documents securely</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card mb-4">
                    <div class="card-header bg-white">
                        <h5 class="mb-0"><i class="bi bi-upload"></i> Upload Document</h5>
                    </div>
                    <div class="card-body">
                        <?php if (!empty($upload_message)): ?>
                            <div class="alert alert-<?php echo $upload_status; ?>" role="alert">
                                <?php echo $upload_message; ?>
                            </div>
                        <?php endif; ?>
                        
                        <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post" enctype="multipart/form-data">
                            <div class="mb-3">
                                <label for="document" class="form-label">Select File</label>
                                <input type="file" name="document" id="document" class="form-control form-control-lg">
                                <div class="form-text">Maximum file size: 10MB. Executable files are blocked.</div>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="bi bi-cloud-arrow-up"></i> Upload File
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <!-- Security Notice -->
                <div class="card mb-4">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0"><i class="bi bi-shield-check"></i> Security Information</h5>
                    </div>
                    <div class="card-body">
                        <p>DocuVault CMS implements the following security measures:</p>
                        <ul>
                            <li>Blocked file types: .exe, .bat, .cmd, .com, .msi</li>
                            <li>File size limit: 10MB maximum</li>
                            <li>Automatic virus scanning (pending implementation)</li>
                        </ul>
                        <p class="text-muted mb-0"><small>DocuVault CMS v2.3.1 - Enterprise Document Management</small></p>
                    </div>
                </div>
            </div>

            <!-- Sidebar Widgets Column -->
            <? include("include/sidebar.php") ?>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
