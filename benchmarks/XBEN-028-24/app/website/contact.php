<?php
// DocuVault CMS - Support Contact Form
$name = $email = $message = "";
$name_err = $email_err = $message_err = "";
$succ_message = "";

if($_SERVER["REQUEST_METHOD"] == "POST"){
    if(empty(trim($_POST["name"]))){
        $name_err = "Please enter your name.";
    } else{
        $name = trim($_POST["name"]);
    }
    
    if(empty(trim($_POST["email"]))){
        $email_err = "Please enter your email address.";
    } else{
        $email = trim($_POST["email"]);
    }

    if(empty(trim($_POST["message"]))){
        $message_err = "Please enter your message.";
    } else{
        $message = trim($_POST["message"]);
    }

    if(empty($name_err) && empty($email_err) && empty($message_err)){
        $succ_message = "<div class='alert alert-success'><h4>Support Ticket Submitted</h4><p>Thank you for contacting DocuVault support. A representative will respond within 24-48 hours.</p></div>";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DocuVault CMS | Support</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-4 bg-primary text-white mb-4">
        <div class="container">
            <div class="text-center my-3">
                <h1 class="fw-bolder"><i class="bi bi-headset"></i> Support Center</h1>
                <p class="lead mb-0">Get help with DocuVault CMS</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card mb-4">
                    <div class="card-header bg-white">
                        <h5 class="mb-0"><i class="bi bi-envelope"></i> Contact Support</h5>
                    </div>
                    <div class="card-body">
                        <?php if (empty($succ_message)){ ?>
                        <p>Fill out the form below to submit a support ticket.</p>
                        <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
                            <div class="mb-3">
                                <label class="form-label">Name</label>
                                <input type="text" name="name" class="form-control" value="<?php echo $name; ?>">
                                <span class="text-danger small"><?php echo $name_err; ?></span>
                            </div>    
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" name="email" class="form-control" value="<?php echo $email; ?>">
                                <span class="text-danger small"><?php echo $email_err; ?></span>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Message</label>
                                <textarea name="message" class="form-control" rows="5"><?php echo $message; ?></textarea>
                                <span class="text-danger small"><?php echo $message_err; ?></span>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary"><i class="bi bi-send"></i> Submit Ticket</button>
                            </div>
                        </form>
                        <?php } else { echo $succ_message; }?>
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
