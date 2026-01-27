<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MyWishlist | About</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <div class="d-flex justify-content-between w-100">
                <a class="navbar-brand" href="/index.php">MyWishlist</a>
                <div>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavAltMarkup">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse justify-content-end" id="navbarNavAltMarkup">
                        <div class="navbar-nav">
                            <a class="nav-link" href="/index.php">Home</a>
                            <a class="nav-link" href="/wishlist.php">My Wishlist</a>
                            <a class="nav-link active" href="/about.php">About</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <!-- Header -->
    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">About MyWishlist</h1>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="container mt-5">
                    <h1>Your Personal Product Manager</h1>
                    <p>
                        MyWishlist is a simple yet powerful tool designed to help you keep track of products 
                        you're interested in purchasing. Whether you're planning for a special occasion, 
                        comparing prices, or just bookmarking items for later, MyWishlist makes it easy.
                    </p>

                    <h2>How It Works</h2>
                    <p>
                        Simply browse our catalog, add items to your wishlist, and organize them however you like.
                        Use our sorting features to view your items by name, price, category, or date added.
                    </p>

                    <h2>Features</h2>
                    <ul>
                        <li><strong>Easy Organization:</strong> Sort your wishlist by multiple criteria</li>
                        <li><strong>Quick Access:</strong> View all your saved items in one place</li>
                        <li><strong>Simple Interface:</strong> Clean, intuitive design</li>
                    </ul>

                    <h2>Technical Details</h2>
                    <p>
                        MyWishlist is built using PHP and SQLite for fast, reliable performance.
                        The application stores product data locally using a lightweight database system.
                    </p>
                    <!-- Database: SQLite3, Tables: products, config -->
                </div>
            </div>
            
            <!-- Sidebar -->
            <div class="col-md-4">
                <div class="card my-4">
                    <h5 class="card-header">Get Started</h5>
                    <div class="card-body">
                        <p>Ready to organize your favorites?</p>
                        <a href="wishlist.php" class="btn btn-primary">View Wishlist</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
