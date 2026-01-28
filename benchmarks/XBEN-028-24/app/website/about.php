<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>eZ Content Hub | Platform Overview</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-5 bg-dark text-white border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Platform Overview</h1>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="container mt-5">
                    <h1>eZ Content Hub Platform</h1>
                    <p>
                        eZ Content Hub is an enterprise-grade content management platform designed for modern digital experiences. Built on proven technology and trusted by organizations worldwide, it provides the tools needed to create, manage, and publish content at scale.
                    </p>

                    <h2>Key Features</h2>
                    <p>
                        Our platform offers comprehensive content management capabilities including multi-language support, advanced workflows, granular permissions, and flexible content modeling. The media library supports various file types including images, documents, and binary files through our ezbinaryfile field type.
                    </p>

                    <h2>Technical Architecture</h2>
                    <p>
                        Built on a robust PHP foundation with a modular architecture, eZ Content Hub integrates seamlessly with existing infrastructure. The platform uses a repository pattern for content storage and provides both REST API and traditional web interfaces for content management.
                    </p>

                    <h2>Security</h2>
                    <p>
                        Security is paramount in enterprise content management. Our platform implements multiple layers of protection including role-based access control, content validation, and file upload filtering. The FileExtensionBlackListValidator ensures that potentially dangerous file types are blocked from upload.
                    </p>

                    <h2>Version Information</h2>
                    <div class="alert alert-info">
                        <strong>Current Version:</strong> 2.3.1-legacy<br>
                        <strong>PHP Version:</strong> <?php echo phpversion(); ?><br>
                        <strong>Server:</strong> <?php echo $_SERVER['SERVER_SOFTWARE'] ?? 'Apache'; ?>
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
