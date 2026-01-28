<?php
    include 'config.php';
?>
<!doctype html>
<html>
    <head>
        <title>NoteHub CRM - About</title>
        <link rel="stylesheet" href="static/styles.css">
        <link rel="icon" href="static/favicon.ico" type="image/x-icon">
    </head>
    <body>
        &nbsp;</br>
        <div class="center blue">
            <div class="logo">NoteHub CRM</div>
            <h1>About NoteHub CRM</h1>
            <table width="100%">
                <tr>
                    <td><strong>Version:</strong></td>
                    <td>5.2.1 Enterprise Edition</td>
                </tr>
                <tr>
                    <td><strong>Build:</strong></td>
                    <td>20240115</td>
                </tr>
                <tr>
                    <td><strong>Database:</strong></td>
                    <td>MySQL/MariaDB</td>
                </tr>
                <tr>
                    <td><strong>PHP Version:</strong></td>
                    <td><?php echo phpversion(); ?></td>
                </tr>
            </table>
            <br>
            <p>NoteHub CRM is a lightweight customer relationship management system designed for small to medium businesses.</p>
            <br>
            <a class="button" href="sign-in.php">Back to Login</a>
        </div>
        <div class="footer">
            <p>&copy; 2024 NoteHub CRM | <a href="about.php">About</a> | <a href="api-docs.php">API</a></p>
        </div>
    </body>
</html>
