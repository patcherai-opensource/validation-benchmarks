<?php
// Article submission is currently disabled - we are migrating to the new CMS
// Contact us at admin@encoder64blog.local if you wish to contribute
$succ_message = "";
$name = $email = "";
$name_err = $email_err = "";
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>Encoder64 Blog | Article Submission</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <? include("../include/navigation-bar.php") ?>

    <!-- Header with Featured Post -->
    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Submit Your Article</h1>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="container mt-5">
                    <div class="alert alert-info">
                        <h4>Article Submission Temporarily Unavailable</h4>
                        <p>We are migrating to our new Content Management System. Article submissions through this form are currently disabled.</p>
                        <p>If you would like to contribute, please contact us at <a href="/contact.php">our contact page</a>.</p>
                    </div>
                </div>
            </div>
        <!-- Sidebar Widgets Column -->
        <? include("../include/sidebar.php") ?>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
