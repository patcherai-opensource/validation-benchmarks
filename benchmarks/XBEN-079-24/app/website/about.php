<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>SolarView | Documentation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .navbar-brand { font-weight: bold; color: #f7931a !important; }
        .bg-solar { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
    </style>
</head>
<body class="bg-light">
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header Section -->
    <header class="py-5 bg-solar text-white border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Documentation</h1>
                <p class="lead">SolarView Dashboard v1.34.2</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="container mt-4">
                    <h2>About SolarView</h2>
                    <p>
                        SolarView is an interactive widget analytics platform built on the widgetti framework. 
                        It provides real-time data visualization, system monitoring, and comprehensive analytics 
                        capabilities for modern web applications.
                    </p>

                    <h3>Features</h3>
                    <ul>
                        <li><strong>Real-Time Visualization:</strong> Interactive charts with live data streaming</li>
                        <li><strong>System Monitoring:</strong> Track CPU, memory, and network metrics</li>
                        <li><strong>Analytics Dashboard:</strong> Comprehensive analytics with drill-down capabilities</li>
                        <li><strong>CDN Integration:</strong> Fast asset delivery through integrated caching</li>
                        <li><strong>Extensible Widgets:</strong> Modular widget architecture for customization</li>
                    </ul>

                    <h3>Architecture</h3>
                    <p>
                        SolarView uses a microservices architecture with the following components:
                    </p>
                    <ul>
                        <li><code>/index.php</code> - Main dashboard entry point</li>
                        <li><code>/widget.php</code> - Widget rendering engine</li>
                        <li><code>/cdn.php</code> - CDN asset caching and delivery</li>
                        <li><code>/static/</code> - Static resource directory</li>
                    </ul>

                    <h3>Version History</h3>
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Version</th>
                                <th>Release Date</th>
                                <th>Notes</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>1.34.2</td>
                                <td>2024-01-15</td>
                                <td>Current release - Performance improvements</td>
                            </tr>
                            <tr>
                                <td>1.34.1</td>
                                <td>2024-01-08</td>
                                <td>Bug fixes for widget rendering</td>
                            </tr>
                            <tr>
                                <td>1.34.0</td>
                                <td>2024-01-01</td>
                                <td>Added CDN caching layer</td>
                            </tr>
                        </tbody>
                    </table>

                    <h3>Configuration</h3>
                    <p>
                        Widget configuration is managed through JSON files in the <code>static/cache/</code> directory.
                        See <code>widget-config.json</code> for available settings.
                    </p>
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
