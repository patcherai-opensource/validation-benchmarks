<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SecureAuth Portal - About</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <?php include("include/navigation-bar.php"); ?>

    <header class="py-5 bg-primary text-white mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">About SecureAuth</h1>
                <p class="lead mb-0">Enterprise Identity Management</p>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="container mt-3">
                    <h2>Our Mission</h2>
                    <p>
                        SecureAuth Portal is a leading enterprise identity management solution designed to provide 
                        secure authentication and authorization services for organizations of all sizes.
                    </p>

                    <h3>Key Features</h3>
                    <ul>
                        <li><strong>Single Sign-On (SSO)</strong> - Access all your applications with one set of credentials</li>
                        <li><strong>Multi-Factor Authentication</strong> - Enhanced security with multiple verification methods</li>
                        <li><strong>Password Management</strong> - Self-service password reset and recovery</li>
                        <li><strong>Audit Logging</strong> - Complete visibility into authentication events</li>
                        <li><strong>API Integration</strong> - RESTful APIs for seamless integration</li>
                    </ul>

                    <h3>Security First</h3>
                    <p>
                        Our platform is built with security at its core. We implement industry best practices 
                        including secure token generation, encrypted communications, and comprehensive access controls.
                    </p>
                    
                    <div class="alert alert-info mt-4">
                        <h5>Technical Information</h5>
                        <p class="mb-0">
                            <strong>Version:</strong> 1.3.3<br>
                            <strong>Framework:</strong> PHP 7.4<br>
                            <strong>Protocol:</strong> HTTP/HTTPS
                        </p>
                    </div>
                </div>
            </div>
            <?php include("include/sidebar.php"); ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
