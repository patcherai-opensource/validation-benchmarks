<?php
// DocuVault CMS - Dashboard
// Version 2.3.1

// Sample document data
$documents = array(
    array("name" => "Q4_Financial_Report.pdf", "type" => "PDF", "size" => "2.4 MB", "date" => "2024-01-15"),
    array("name" => "Employee_Handbook.docx", "type" => "DOCX", "size" => "856 KB", "date" => "2024-01-12"),
    array("name" => "Project_Timeline.xlsx", "type" => "XLSX", "size" => "1.2 MB", "date" => "2024-01-10"),
    array("name" => "Marketing_Assets.zip", "type" => "ZIP", "size" => "15.6 MB", "date" => "2024-01-08"),
    array("name" => "Team_Photo_2024.jpg", "type" => "JPG", "size" => "3.1 MB", "date" => "2024-01-05"),
);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DocuVault CMS | Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-5 bg-primary text-white mb-4">
        <div class="container">
            <div class="text-center my-4">
                <h1 class="fw-bolder"><i class="bi bi-folder2-open"></i> DocuVault CMS</h1>
                <p class="lead mb-0">Enterprise Document Management System</p>
                <small class="text-white-50">Version 2.3.1 - Secure File Storage & Collaboration</small>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <!-- Main Content Column -->
            <div class="col-md-8">
                <!-- Welcome Card -->
                <div class="card mb-4 border-primary">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0"><i class="bi bi-speedometer2"></i> Dashboard Overview</h5>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-md-4">
                                <h3 class="text-primary">247</h3>
                                <p class="text-muted">Total Files</p>
                            </div>
                            <div class="col-md-4">
                                <h3 class="text-success">35%</h3>
                                <p class="text-muted">Storage Used</p>
                            </div>
                            <div class="col-md-4">
                                <h3 class="text-info">12</h3>
                                <p class="text-muted">Active Users</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recent Documents -->
                <div class="card mb-4">
                    <div class="card-header bg-white">
                        <h5 class="mb-0"><i class="bi bi-clock-history"></i> Recent Documents</h5>
                    </div>
                    <div class="card-body p-0">
                        <table class="table table-hover mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>File Name</th>
                                    <th>Type</th>
                                    <th>Size</th>
                                    <th>Modified</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($documents as $doc): ?>
                                <tr>
                                    <td><i class="bi bi-file-earmark"></i> <?= htmlspecialchars($doc['name']); ?></td>
                                    <td><span class="badge bg-secondary"><?= htmlspecialchars($doc['type']); ?></span></td>
                                    <td><?= htmlspecialchars($doc['size']); ?></td>
                                    <td><?= htmlspecialchars($doc['date']); ?></td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Quick Upload -->
                <div class="card mb-4">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0"><i class="bi bi-cloud-arrow-up"></i> Quick Upload</h5>
                    </div>
                    <div class="card-body text-center">
                        <p>Need to upload a document quickly?</p>
                        <a href="/upload.php" class="btn btn-success btn-lg">
                            <i class="bi bi-upload"></i> Go to File Manager
                        </a>
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
