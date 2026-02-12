<?php
$page_title = "DevCore Solutions - Enterprise Software Consulting";
$current_year = date('Y');

// Simple routing
$page = isset($_GET['page']) ? $_GET['page'] : 'home';
$allowed_pages = ['home', 'about', 'services', 'portfolio', 'contact'];

if (!in_array($page, $allowed_pages)) {
    $page = 'home';
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($page_title); ?></title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="/?page=home">DevCore Solutions</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ml-auto">
                    <li class="nav-item <?php echo $page === 'home' ? 'active' : ''; ?>">
                        <a class="nav-link" href="/?page=home">Home</a>
                    </li>
                    <li class="nav-item <?php echo $page === 'about' ? 'active' : ''; ?>">
                        <a class="nav-link" href="/?page=about">About</a>
                    </li>
                    <li class="nav-item <?php echo $page === 'services' ? 'active' : ''; ?>">
                        <a class="nav-link" href="/?page=services">Services</a>
                    </li>
                    <li class="nav-item <?php echo $page === 'portfolio' ? 'active' : ''; ?>">
                        <a class="nav-link" href="/?page=portfolio">Portfolio</a>
                    </li>
                    <li class="nav-item <?php echo $page === 'contact' ? 'active' : ''; ?>">
                        <a class="nav-link" href="/?page=contact">Contact</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="mt-5 pt-3">
    <?php
    switch ($page) {
        case 'home':
            include 'pages/home.php';
            break;
        case 'about':
            include 'pages/about.php';
            break;
        case 'services':
            include 'pages/services.php';
            break;
        case 'portfolio':
            include 'pages/portfolio.php';
            break;
        case 'contact':
            include 'pages/contact.php';
            break;
    }
    ?>
    </main>

    <footer class="bg-dark text-white text-center py-4 mt-5">
        <div class="container">
            <p class="mb-0">&copy; <?php echo $current_year; ?> DevCore Solutions. All rights reserved.</p>
            <small>Enterprise Software Consulting &amp; Development</small>
        </div>
    </footer>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
