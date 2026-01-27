<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DocuVault CMS | Documentation</title>
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
                <h1 class="fw-bolder"><i class="bi bi-book"></i> Documentation</h1>
                <p class="lead mb-0">Learn how to use DocuVault CMS</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card mb-4">
                    <div class="card-body">
                        <h2><i class="bi bi-info-circle"></i> About DocuVault CMS</h2>
                        <p>
                            DocuVault CMS is an enterprise-grade document management system designed for teams that need secure, reliable file storage and collaboration. Built with modern web technologies, it provides a seamless experience for uploading, organizing, and sharing documents.
                        </p>

                        <h3>Key Features</h3>
                        <ul>
                            <li><strong>Easy File Upload:</strong> Drag and drop or browse to upload documents</li>
                            <li><strong>Secure Storage:</strong> Files are stored with enterprise-grade security</li>
                            <li><strong>Access Control:</strong> Manage who can view and edit documents</li>
                            <li><strong>Version History:</strong> Track changes and restore previous versions</li>
                        </ul>

                        <h3>File Upload Guidelines</h3>
                        <p>
                            DocuVault CMS accepts most document types including PDFs, Office documents, images, and archives. For security reasons, certain executable file types are blocked:
                        </p>
                        <ul>
                            <li>.exe - Windows Executables</li>
                            <li>.bat - Batch Files</li>
                            <li>.cmd - Command Scripts</li>
                            <li>.com - DOS Executables</li>
                            <li>.msi - Windows Installer Packages</li>
                        </ul>

                        <h3>API Access</h3>
                        <p>
                            DocuVault provides RESTful API access for integration with other systems. Contact your administrator for API credentials and documentation.
                        </p>

                        <h3>Technical Specifications</h3>
                        <table class="table table-bordered">
                            <tr><td><strong>Version</strong></td><td>2.3.1</td></tr>
                            <tr><td><strong>Max File Size</strong></td><td>10 MB</td></tr>
                            <tr><td><strong>Storage Backend</strong></td><td>Local Filesystem</td></tr>
                            <tr><td><strong>Web Server</strong></td><td>Apache 2.4</td></tr>
                            <tr><td><strong>PHP Version</strong></td><td>7.4+</td></tr>
                        </table>
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
