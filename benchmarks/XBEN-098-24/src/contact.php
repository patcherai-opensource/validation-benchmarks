<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact - DBAdmin</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <img src="images/logo.png" width="120" height="100">
        </div>
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/about.php">About</a></li>
            <li><a href="/contact.php">Contact</a></li>
            <li><a href="/connect.php">Connect</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>Contact & Support</h1>
        <?php
        error_reporting(0);
        if ($_SERVER["REQUEST_METHOD"] == "POST") {
            $name = htmlspecialchars($_POST['name']);
            $email = htmlspecialchars($_POST['email']);
            $message = htmlspecialchars($_POST['message']);

            echo "<p>Thanks for your feedback. Our support team will review your message and respond within 24-48 hours.</p>";
        } else {
        ?>
        <p>Have questions about DBAdmin? Found a bug? Need help with configuration? Use the form below to get in touch with our support team.</p>
        
        <form action="contact.php" method="post">
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" required>
            
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
            
            <label for="message">Message:</label>
            <textarea id="message" name="message" rows="6" required></textarea>
            
            <input type="submit" value="Submit">
        </form>
        
        <div style="margin-top: 30px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 5px;">
            <h3>Documentation</h3>
            <p>For common questions and setup guides, please refer to our documentation:</p>
            <ul style="color: #ccc;">
                <li>Getting Started Guide</li>
                <li>Configuration Options</li>
                <li>Troubleshooting Connection Issues</li>
                <li>Security Best Practices</li>
            </ul>
        </div>
        <?php
        }
        ?>
    </div>
</body>
</html>

