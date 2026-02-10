<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit - <?php echo isset($page_title) ? htmlspecialchars($page_title) : 'Wiki'; ?></title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <img src="/images/logo.png" width="120" height="100">
        </div>
        <ul>
            <li><a href="/?page=HomePage">Home</a></li>
            <li><a href="/?page=AboutPage">About</a></li>
            <li><a href="/?page=ContactPage">Contact</a></li>
            <li><a href="/?page=LoginPage">Login</a></li>
        </ul>
    </div>
    <div class="content">
        <h2>Edit: <?php echo isset($page_title) ? htmlspecialchars($page_title) : ''; ?></h2>
        <form method="post" action="/?page=<?php echo urlencode($page_name ?? ''); ?>/edit">
            <textarea name="body" rows="20" cols="80"><?php echo isset($page_body) ? htmlspecialchars($page_body) : ''; ?></textarea>
            <br><br>
            <input type="submit" value="Save Changes">
        </form>
    </div>
</body>
</html>
