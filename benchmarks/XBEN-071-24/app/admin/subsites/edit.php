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

$id = (int)($_GET['id'] ?? 0);
$message = '';
$messageType = '';

if (isset($_POST['action']) && $_POST['action'] === 'update_subsite') {
    $id = (int)($_POST['ID'] ?? 0);
    $title = $_POST['Title'] ?? '';
    $domain = $_POST['Domain'] ?? '';
    $theme = $_POST['Theme'] ?? 'default';

    if ($id > 0 && !empty($title)) {
        $stmt = $conn->prepare("UPDATE Subsite SET Title = ?, Domain = ?, Theme = ? WHERE ID = ?");
        $stmt->bind_param("sssi", $title, $domain, $theme, $id);
        $stmt->execute();
        $message = 'Subsite updated successfully.';
        $messageType = 'success';
        $stmt->close();
    }
}

$subsite = null;
if ($id > 0) {
    $stmt = $conn->prepare("SELECT * FROM Subsite WHERE ID = ?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    $subsite = $result->fetch_assoc();
    $stmt->close();
}

$conn->close();

if (!$subsite) {
    header("Location: /admin/subsites/");
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Subsite - CMS Admin</title>
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
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 13px; font-weight: 500; margin-bottom: 4px; color: #666; }
        .form-group input, .form-group select { width: 100%; padding: 8px 10px; border: 1px solid #ccc; border-radius: 3px; font-size: 14px; }
        .btn { display: inline-block; padding: 8px 20px; border: none; border-radius: 3px; font-size: 14px; cursor: pointer; text-decoration: none; }
        .btn-action { background: #005a93; color: #fff; }
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
        <h2>Edit Subsite</h2>

        <?php if ($message): ?>
            <div class="alert alert-<?php echo $messageType; ?>"><?php echo htmlspecialchars($message); ?></div>
        <?php endif; ?>

        <form method="POST" action="/admin/subsites/edit.php?id=<?php echo (int)$subsite['ID']; ?>">
            <input type="hidden" name="action" value="update_subsite">
            <input type="hidden" name="ID" value="<?php echo (int)$subsite['ID']; ?>">
            <div class="form-group">
                <label for="Title">Subsite Name</label>
                <input type="text" name="Title" id="Title" value="<?php echo htmlspecialchars($subsite['Title']); ?>" required>
            </div>
            <div class="form-group">
                <label for="Domain">Domain</label>
                <input type="text" name="Domain" id="Domain" value="<?php echo htmlspecialchars($subsite['Domain']); ?>" required>
            </div>
            <div class="form-group">
                <label for="Theme">Theme</label>
                <select name="Theme" id="Theme">
                    <option value="default" <?php echo ($subsite['Theme'] === 'default') ? 'selected' : ''; ?>>Default</option>
                    <option value="simple" <?php echo ($subsite['Theme'] === 'simple') ? 'selected' : ''; ?>>Simple</option>
                    <option value="starter" <?php echo ($subsite['Theme'] === 'starter') ? 'selected' : ''; ?>>Starter</option>
                </select>
            </div>
            <button type="submit" class="btn btn-action">Save</button>
            <a href="/admin/subsites/" class="btn btn-back">Cancel</a>
        </form>
    </div>
</body>
</html>
