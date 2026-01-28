<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Support - DataLabel Studio</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <img src="images/logo.png" width="120" height="100">
        </div>
        <ul>
            <li><a href="/">Dashboard</a></li>
            <li><a href="/projects.php">Projects</a></li>
            <li><a href="/tasks.php">Tasks</a></li>
            <li><a href="/export.php">Export</a></li>
            <li><a href="/about.php">About</a></li>
            <li><a href="/login.php">Login</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>Support</h1>
        <?php
        if ($_SERVER["REQUEST_METHOD"] == "POST") {
            $name = htmlspecialchars($_POST['name']);
            $email = htmlspecialchars($_POST['email']);
            $message = htmlspecialchars($_POST['message']);

            echo "<p>Thank you for contacting DataLabel Studio support. A member of our team will respond within 24 hours.</p>";
        } else {
        ?>
        <p>Need help with DataLabel Studio? Fill out the form below or check our resources.</p>

        <h3>Resources</h3>
        <ul>
            <li><a href="/api/docs.php">API Documentation</a></li>
            <li><a href="https://docs.datalabel.io">User Guide</a></li>
            <li><a href="https://community.datalabel.io">Community Forum</a></li>
            <li><a href="https://status.datalabel.io">System Status</a></li>
        </ul>

        <h3>Contact Support</h3>
        <form action="contact.php" method="post">
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" required>
            
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
            
            <label for="category">Category:</label>
            <select id="category" name="category">
                <option value="general">General Inquiry</option>
                <option value="technical">Technical Support</option>
                <option value="billing">Billing</option>
                <option value="enterprise">Enterprise Sales</option>
            </select>
            
            <label for="message">Message:</label>
            <textarea id="message" name="message" required></textarea>
            
            <input type="submit" value="Submit Request">
        </form>
        <?php
        }
        ?>
    </div>
</body>
</html>

