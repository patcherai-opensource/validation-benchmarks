<?php
session_start();

if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header("Location: /admin/login.php");
    exit;
}

$servername = $_ENV['DB_HOST'] ?? "127.0.0.1";
$username_db = $_ENV['DB_USER'] ?? "challenge";
$password_db = $_ENV['DB_PASSWORD'] ?? "challenge";
$dbname = $_ENV['DB_NAME'] ?? "challenge";

$conn = new mysqli($servername, $username_db, $password_db, $dbname);
if ($conn->connect_error) {
    die("Database connection error.");
}

$message = '';
$messageType = '';

if (isset($_POST['action']) && $_POST['action'] === 'create_subsite') {
    $title = $_POST['Title'] ?? '';
    $domain = $_POST['Domain'] ?? '';
    $theme = $_POST['Theme'] ?? 'default';

    if (!empty($title) && !empty($domain)) {
        $stmt = $conn->prepare("INSERT INTO Subsite (Title, Domain, IsDefault, Theme) VALUES (?, ?, 0, ?)");
        $stmt->bind_param("sss", $title, $domain, $theme);
        $stmt->execute();

        if ($stmt->affected_rows > 0) {
            $message = 'Subsite created successfully.';
            $messageType = 'success';
        } else {
            $message = 'Failed to create subsite.';
            $messageType = 'warning';
        }
        $stmt->close();
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Subsite - CMS Admin</title>
    <link rel="icon" href="/favicon.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .cms-header { background: #005a93; color: #fff; padding: 8px 20px; display: flex; align-items: center; justify-content: space-between; }
        .cms-header h1 { font-size: 16px; font-weight: 400; }
        .cms-header .user-info { font-size: 13px; }
        .cms-header a { color: #cce; text-decoration: none; }
        .cms-nav { background: #004570; padding: 0 20px; }
        .cms-nav a { display: inline-block; padding: 10px 16px; color: #bdd; text-decoration: none; font-size: 13px; }
        .cms-nav a:hover, .cms-nav a.active { background: rgba(255,255,255,0.1); color: #fff; }
        .cms-content { max-width: 600px; margin: 20px auto; padding: 0 20px; }
        .cms-content h2 { font-size: 20px; font-weight: 400; margin-bottom: 16px; }
        .alert { padding: 10px 14px; border-radius: 3px; margin-bottom: 16px; font-size: 13px; }
        .alert-success { background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
        .alert-warning { background: #fff8e1; color: #f57f17; border: 1px solid #ffecb3; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 13px; font-weight: 500; margin-bottom: 4px; color: #666; }
        .form-group input, .form-group select { width: 100%; padding: 8px 10px; border: 1px solid #ccc; border-radius: 3px; font-size: 14px; }
        .btn { display: inline-block; padding: 8px 20px; border: none; border-radius: 3px; font-size: 14px; cursor: pointer; text-decoration: none; }
        .btn-action { background: #005a93; color: #fff; }
        .btn-action:hover { background: #004570; }
        .btn-back { color: #005a93; padding: 8px 0; }
    </style>
</head>
<body>
    <div class="cms-header">
        <h1>SilverCMS</h1>
        <div class="user-info">
            <?php echo htmlspecialchars($_SESSION['member_name']); ?> |
            <a href="/admin/logout.php">Log out</a>
        </div>
    </div>
    <div class="cms-nav">
        <a href="/admin/pages/">Pages</a>
        <a href="/admin/subsites/" class="active">Subsites</a>
        <a href="/admin/groups/">Groups</a>
        <a href="/admin/settings/">Settings</a>
    </div>
    <div class="cms-content">
        <h2>Create Subsite</h2>

        <?php if ($message): ?>
            <div class="alert alert-<?php echo $messageType; ?>"><?php echo htmlspecialchars($message); ?></div>
        <?php endif; ?>

        <form method="POST" action="/admin/subsites/create.php">
            <input type="hidden" name="action" value="create_subsite">
            <div class="form-group">
                <label for="Title">Subsite Name</label>
                <input type="text" name="Title" id="Title" required>
            </div>
            <div class="form-group">
                <label for="Domain">Domain</label>
                <input type="text" name="Domain" id="Domain" placeholder="e.g. subdomain.example.com" required>
            </div>
            <div class="form-group">
                <label for="Theme">Theme</label>
                <select name="Theme" id="Theme">
                    <option value="default">Default</option>
                    <option value="simple">Simple</option>
                    <option value="starter">Starter</option>
                </select>
            </div>
            <button type="submit" class="btn btn-action">Create Subsite</button>
            <a href="/admin/subsites/" class="btn btn-back">Cancel</a>
        </form>
    </div>
</body>
</html>
