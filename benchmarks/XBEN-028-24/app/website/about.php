<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpringDocs - About</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .hero-section { background: linear-gradient(135deg, #6DB33F 0%, #34302D 100%); color: white; }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <strong>SpringDocs</strong>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="/resources.php?file=docs/readme.txt">Documentation</a></li>
                    <li class="nav-item"><a class="nav-link active" href="/about.php">About</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <header class="hero-section py-5">
        <div class="container text-center">
            <h1 class="display-4 fw-bold">About SpringDocs</h1>
            <p class="lead">Built on Spring Framework's Functional Web Framework</p>
        </div>
    </header>

    <!-- Main Content -->
    <div class="container my-5">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <h2>Spring Framework Functional Web Framework</h2>
                <p>
                    SpringDocs leverages Spring Framework's functional web routing capabilities through 
                    <code>WebMvc.fn</code> to serve static resources efficiently and securely.
                </p>

                <h3 class="mt-4">Architecture</h3>
                <p>
                    The application uses <code>RouterFunctions</code> with <code>FileSystemResource</code> 
                    to serve documentation files from a designated public directory. This pattern provides 
                    a clean, functional approach to handling HTTP requests.
                </p>

                <h3 class="mt-4">Resource Handling</h3>
                <p>
                    Static resources are served through a dedicated endpoint that maps file requests to 
                    the underlying filesystem. The router validates requested paths and serves appropriate 
                    content types based on file extensions.
                </p>

                <div class="card mt-4">
                    <div class="card-header">
                        <strong>Technical Details</strong>
                    </div>
                    <div class="card-body">
                        <ul class="mb-0">
                            <li><strong>Framework:</strong> Spring Framework 5.3.18</li>
                            <li><strong>Module:</strong> spring-webmvc (WebMvc.fn)</li>
                            <li><strong>Resource Type:</strong> FileSystemResource</li>
                            <li><strong>Routing:</strong> RouterFunctions.resources()</li>
                            <li><strong>Base Path:</strong> /public/</li>
                        </ul>
                    </div>
                </div>

                <h3 class="mt-4">Security Considerations</h3>
                <p>
                    Path traversal protection is implemented to prevent unauthorized access to files 
                    outside the designated public directory. The system validates incoming paths and 
                    blocks requests containing traversal sequences.
                </p>

                <div class="alert alert-info mt-4">
                    <strong>Note:</strong> For production deployments, we recommend enabling Spring Security's 
                    HTTP Firewall for additional protection, or running behind Tomcat/Jetty which provide 
                    built-in request filtering.
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="bg-dark text-white py-4 mt-5">
        <div class="container text-center">
            <p class="mb-0">&copy; 2024 SpringDocs. Powered by Spring Framework.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
