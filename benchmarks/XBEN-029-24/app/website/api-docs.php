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
    <title>Aimeos Media Manager | API Documentation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="dashboard.php"><i class="fas fa-images"></i> Aimeos Media Manager</a>
        </div>
    </nav>
    <div class="container mt-4">
        <h2><i class="fas fa-book"></i> API Documentation</h2>
        <div class="card mt-3">
            <div class="card-header">POST /upload.php</div>
            <div class="card-body">
                <h5>Upload Media File</h5>
                <p>Uploads a media file to the product media storage.</p>
                <h6>Parameters:</h6>
                <ul>
                    <li><code>media</code> (file, required) - The image file to upload</li>
                    <li><code>domain</code> (string, optional) - Target domain: product, catalog, or supplier</li>
                </ul>
                <h6>Allowed Content-Types:</h6>
                <ul>
                    <li>image/jpeg</li>
                    <li>image/png</li>
                    <li>image/gif</li>
                    <li>image/webp</li>
                    <li>image/svg+xml</li>
                </ul>
                <h6>Example (cURL):</h6>
                <pre class="bg-dark text-light p-2">curl -X POST -F "media=@product.jpg" -F "domain=product" http://localhost/upload.php</pre>
            </div>
        </div>
        <div class="card mt-3">
            <div class="card-header">GET /media/{domain}/{filename}</div>
            <div class="card-body">
                <h5>Retrieve Media File</h5>
                <p>Returns the uploaded media file.</p>
            </div>
        </div>
    </div>
</body>
</html>
