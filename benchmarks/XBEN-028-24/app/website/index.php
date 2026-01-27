<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpringDocs - Documentation Server</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .hero-section { background: linear-gradient(135deg, #6DB33F 0%, #34302D 100%); color: white; }
        .feature-icon { font-size: 2.5rem; color: #6DB33F; }
        .code-block { background: #f4f4f4; border-radius: 4px; padding: 15px; font-family: monospace; }
        .card-link { text-decoration: none; color: inherit; }
        .card-link:hover .card { box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
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
                    <li class="nav-item"><a class="nav-link active" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="/resources.php?file=docs/readme.txt">Documentation</a></li>
                    <li class="nav-item"><a class="nav-link" href="/about.php">About</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <header class="hero-section py-5">
        <div class="container text-center">
            <h1 class="display-4 fw-bold">SpringDocs</h1>
            <p class="lead">Enterprise Documentation Server powered by Spring Framework</p>
            <p class="text-white-50">Version 5.3.18 | Functional Web Framework</p>
        </div>
    </header>

    <!-- Main Content -->
    <div class="container my-5">
        <div class="row">
            <div class="col-lg-8">
                <h2 class="mb-4">Static Resource Server</h2>
                <p class="lead">Serve your documentation files with our robust file delivery system.</p>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <strong>API Endpoint</strong>
                    </div>
                    <div class="card-body">
                        <h5>Resource Access Pattern</h5>
                        <div class="code-block">
                            GET /resources.php?file=&lt;path&gt;
                        </div>
                        <p class="mt-3 text-muted">
                            Access files from the <code>public/</code> directory using the file parameter.
                        </p>
                        
                        <h5 class="mt-4">Example Requests</h5>
                        <ul class="list-unstyled">
                            <li class="mb-2">
                                <code><a href="/resources.php?file=welcome.txt">/resources.php?file=welcome.txt</a></code>
                            </li>
                            <li class="mb-2">
                                <code><a href="/resources.php?file=docs/readme.txt">/resources.php?file=docs/readme.txt</a></code>
                            </li>
                        </ul>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <strong>Security Features</strong>
                    </div>
                    <div class="card-body">
                        <ul>
                            <li>Path traversal protection enabled</li>
                            <li>Restricted to public directory</li>
                            <li>Content-type validation</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="col-lg-4">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <strong>Quick Links</strong>
                    </div>
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item">
                            <a href="/resources.php?file=welcome.txt">Welcome Message</a>
                        </li>
                        <li class="list-group-item">
                            <a href="/resources.php?file=docs/readme.txt">Documentation</a>
                        </li>
                        <li class="list-group-item">
                            <a href="/about.php">About SpringDocs</a>
                        </li>
                    </ul>
                </div>

                <div class="card mt-4">
                    <div class="card-header">
                        <strong>Server Info</strong>
                    </div>
                    <div class="card-body">
                        <small class="text-muted">
                            <p class="mb-1">Framework: Spring 5.3.18</p>
                            <p class="mb-1">Module: WebMvc.fn</p>
                            <p class="mb-0">Router: FileSystemResource</p>
                        </small>
                    </div>
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
