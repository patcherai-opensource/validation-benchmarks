<?php
/**
 * CMS Admin Panel - Database Migration Tool
 * 
 * This tool helps administrators manage database records across different subsites.
 * It provides functionality to synchronize groups and permissions between subsites.
 */

session_start();

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Simple authentication check (any valid admin user)
$authenticated = false;
if (isset($_SESSION['cms_admin']) && $_SESSION['cms_admin'] === true) {
    $authenticated = true;
}

// Handle login
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
    $username = mysqli_real_escape_string($conn, $_POST['username']);
    $password = mysqli_real_escape_string($conn, $_POST['password']);
    
    $sql = "SELECT id, username FROM cms_users WHERE username = '$username' AND password = '$password'";
    $result = $conn->query($sql);
    
    if ($result && $result->num_rows == 1) {
        $_SESSION['cms_admin'] = true;
        $_SESSION['cms_user'] = $result->fetch_assoc()['username'];
        $authenticated = true;
    } else {
        $login_error = "Invalid credentials";
    }
}

// Handle logout
if (isset($_GET['logout'])) {
    session_destroy();
    header("Location: index.php");
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMS Admin - Database Migration Tool</title>
    <link rel="stylesheet" href="../styles.css">
    <style>
        .admin-panel { max-width: 900px; margin: 20px auto; padding: 20px; }
        .panel-section { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .result { background: #e8f5e9; padding: 10px; margin: 10px 0; border-left: 4px solid #4caf50; }
        .error { background: #ffebee; border-left-color: #f44336; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #333; color: white; }
        code { background: #eee; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
<div class="admin-panel">
    <h1>CMS Admin Panel</h1>
    <p><a href="../">← Back to Blog</a></p>
    
    <?php if (!$authenticated): ?>
    
    <div class="panel-section">
        <h2>Login Required</h2>
        <p>Please login with your CMS admin credentials.</p>
        <?php if (isset($login_error)): ?>
            <p style="color: red;"><?php echo $login_error; ?></p>
        <?php endif; ?>
        <form method="POST">
            <input type="hidden" name="login" value="1">
            <label>Username:</label><br>
            <input type="text" name="username" required><br><br>
            <label>Password:</label><br>
            <input type="password" name="password" required><br><br>
            <button type="submit">Login</button>
        </form>
    </div>
    
    <?php else: ?>
    
    <p>Logged in as: <strong><?php echo htmlspecialchars($_SESSION['cms_user']); ?></strong> | <a href="?logout">Logout</a></p>
    
    <div class="panel-section">
        <h2>Database Migration Tool</h2>
        <p>This tool runs database migrations to synchronize groups and subsites.</p>
        <p>Use the <code>group_class</code> parameter to specify which group table to migrate.</p>
        
        <form method="GET">
            <label>Group Class/Table Name:</label><br>
            <input type="text" name="group_class" value="<?php echo isset($_GET['group_class']) ? htmlspecialchars($_GET['group_class']) : 'groups'; ?>" style="width: 300px;"><br><br>
            <button type="submit">Run Migration</button>
        </form>
    </div>
    
    <?php
    // Database migration functionality - vulnerable to SQL injection
    // Similar to silverstripe/subsites GroupSubsites.php requireDefaultRecords()
    if (isset($_GET['group_class']) && !empty($_GET['group_class'])):
        $groupTable = $_GET['group_class'];
        
        // Simulating the SilverStripe vulnerability:
        // The table name is used directly without escaping, allowing SQL injection
        // Original vulnerable code pattern:
        // DB::query('SELECT "ID", "SubsiteID" FROM "' . $groupTable . '" WHERE "SubsiteID" > 0');
        
        echo '<div class="panel-section">';
        echo '<h3>Migration Results for: <code>' . htmlspecialchars($groupTable) . '</code></h3>';
        
        // Vulnerable query - table name is not escaped (similar to CVE)
        // This simulates: DB::query('SELECT ... FROM "' . $groupTable . '" ...')
        $query = "SELECT id, name, subsite_id FROM " . $groupTable . " WHERE subsite_id > 0";
        
        echo '<p>Executing: <code>' . htmlspecialchars($query) . '</code></p>';
        
        $result = $conn->query($query);
        
        if ($result === false) {
            echo '<div class="result error">';
            echo '<strong>Query Error:</strong> ' . htmlspecialchars($conn->error);
            echo '</div>';
        } else {
            echo '<div class="result">';
            echo '<strong>Query executed successfully.</strong><br>';
            echo 'Rows affected: ' . $result->num_rows . '<br><br>';
            
            if ($result->num_rows > 0) {
                echo '<table>';
                echo '<tr><th>ID</th><th>Name</th><th>Subsite ID</th></tr>';
                while ($row = $result->fetch_assoc()) {
                    echo '<tr>';
                    echo '<td>' . htmlspecialchars($row['id'] ?? '') . '</td>';
                    echo '<td>' . htmlspecialchars($row['name'] ?? '') . '</td>';
                    echo '<td>' . htmlspecialchars($row['subsite_id'] ?? '') . '</td>';
                    echo '</tr>';
                }
                echo '</table>';
            } else {
                echo 'No records found matching criteria.';
            }
            echo '</div>';
        }
        echo '</div>';
    endif;
    ?>
    
    <div class="panel-section">
        <h2>Available Tables</h2>
        <p>Reference list of tables that can be used with the migration tool:</p>
        <ul>
            <li><code>groups</code> - User groups</li>
            <li><code>group_subsites</code> - Group-subsite associations</li>
            <li><code>subsites</code> - Subsite definitions</li>
        </ul>
    </div>
    
    <?php endif; ?>
    
</div>
</body>
</html>
<?php $conn->close(); ?>