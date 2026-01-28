<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EduLearn LMS | About</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-4 bg-dark text-white mb-4">
        <div class="container">
            <h2 class="fw-bolder">About EduLearn LMS</h2>
            <p class="mb-0">Empowering educators and learners worldwide</p>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card mb-4">
                    <div class="card-body">
                        <h3>Our Platform</h3>
                        <p>
                            EduLearn LMS is a comprehensive learning management system designed to facilitate 
                            online education at scale. Built with modern web technologies and a focus on 
                            extensibility, our platform serves educational institutions worldwide.
                        </p>

                        <h4>Key Features</h4>
                        <ul>
                            <li><strong>Course Management:</strong> Create and organize courses with rich multimedia content</li>
                            <li><strong>Database Activities:</strong> Build structured data collections with custom field types</li>
                            <li><strong>Assignment Tracking:</strong> Manage submissions and automated grading</li>
                            <li><strong>Discussion Forums:</strong> Foster collaboration among students</li>
                            <li><strong>Quiz Engine:</strong> Create interactive assessments with various question types</li>
                        </ul>

                        <h4>Architecture</h4>
                        <p>
                            EduLearn is built on a modular architecture allowing for easy extension and 
                            customization. Each module can be independently configured and field types 
                            can be dynamically loaded from the <code>/field</code> directory structure.
                        </p>

                        <h4>Version Information</h4>
                        <table class="table table-sm">
                            <tr><td>Platform Version</td><td>4.3.2</td></tr>
                            <tr><td>Database Module</td><td>2024042200</td></tr>
                            <tr><td>PHP Version</td><td><?= phpversion() ?></td></tr>
                            <tr><td>Server</td><td><?= $_SERVER['SERVER_SOFTWARE'] ?? 'N/A' ?></td></tr>
                        </table>

                        <h4>Open Source</h4>
                        <p>
                            EduLearn is released under an open source license. We encourage security 
                            researchers to responsibly disclose any vulnerabilities found in our platform.
                        </p>
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
