<?php
// Define variables and initialize with empty values
$name = $email = $message = "";
$name_err = $email_err = $message_err = "";
$succ_message = "";
// Processing form data when form is submitted
if($_SERVER["REQUEST_METHOD"] == "POST"){
    // Validate name
    if(empty(trim($_POST["name"]))){
        $name_err = "Please enter your name.";
    } else{
        $name = trim($_POST["name"]);
    }
    
    // Validate email
    if(empty(trim($_POST["email"]))){
        $email_err = "Please enter your email address.";
    } else{
        $email = trim($_POST["email"]);
    }

    // Validate message
    if(empty(trim($_POST["message"]))){
        $message_err = "Please enter your message.";
    } else{
        $message = trim($_POST["message"]);
    }

    // Check input errors before showing message
    if(empty($name_err) && empty($email_err) && empty($message_err)){
        $succ_message = "<div class='alert alert-success'><h4>Support Request Submitted</h4><p>Thank you for contacting SolarView support. We will respond within 24-48 hours.</p></div>";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>SolarView | Support</title>
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
                <h1 class="fw-bolder">Support Center</h1>
                <p class="lead">Get help with SolarView Dashboard</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="container mt-4">
                    <?php if (empty($succ_message)){ ?>
                    <h4>Submit a Support Request</h4>
                    <p>Fill out the form below and our team will assist you.</p>
                    <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
                        <div class="form-group mb-3">
                            <label>Name</label>
                            <input type="text" name="name" class="form-control" value="<?php echo $name; ?>">
                            <span class="text-danger"><?php echo $name_err; ?></span>
                        </div>    
                        <div class="form-group mb-3">
                            <label>Email</label>
                            <input type="email" name="email" class="form-control" value="<?php echo $email; ?>">
                            <span class="text-danger"><?php echo $email_err; ?></span>
                        </div>
                        <div class="form-group mb-3">
                            <label>Message</label>
                            <textarea name="message" class="form-control" rows="5"><?php echo $message; ?></textarea>
                            <span class="text-danger"><?php echo $message_err; ?></span>
                        </div>
                        <div class="form-group">
                            <input type="submit" class="btn btn-warning" value="Submit Request">
                        </div>
                    </form>
                    <?php } else { echo $succ_message; }?>
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
