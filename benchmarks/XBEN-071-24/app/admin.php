<?php
session_start();

// Database connection helper
function getDbConnection() {
    $servername = $_ENV['DB_HOST'] ?? "localhost";
    $username = $_ENV['DB_USER'] ?? "challenge";
    $password = $_ENV['DB_PASSWORD'] ?? "challenge";
    $dbname = $_ENV['DB_NAME'] ?? "challenge";
    
    $conn = new mysqli($servername, $username, $password, $dbname);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    return $conn;
}

// Check if user is logged in
if (!isset($_SESSION['user_id'])) {
    header("Location: send.php");
    exit;
}

$conn = getDbConnection();
$user_id = $_SESSION['user_id'];
$username = $_SESSION['username'];

// Get user permissions
$stmt = $conn->prepare("SELECT can_view_faq, can_edit_faq, can_add_faq, is_admin FROM users WHERE id = ?");
$stmt->bind_param("i", $user_id);
$stmt->execute();
$result = $stmt->get_result();
$permissions = $result->fetch_assoc();

$can_view = $permissions['can_view_faq'];
$can_edit = $permissions['can_edit_faq'];
$can_add = $permissions['can_add_faq'];
$is_admin = $permissions['is_admin'];

// Get current action
$action = $_GET['action'] ?? 'dashboard';

// Message handling
$message = '';
$message_type = '';

// Handle FAQ operations
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['edit_faq']) && $can_edit) {
        // Edit existing FAQ - allowed for users with edit permission
        $faq_id = intval($_POST['faq_id']);
        $question = $_POST['question'];
        $answer = $_POST['answer'];
        
        $stmt = $conn->prepare("UPDATE faqs SET question = ?, answer = ? WHERE id = ?");
        $stmt->bind_param("ssi", $question, $answer, $faq_id);
        $stmt->execute();
        
        $message = "FAQ updated successfully!";
        $message_type = "success";
    }
    
    if (isset($_POST['add_faq'])) {
        // VULNERABLE CODE: This is the business logic flaw
        // The permission check uses OR instead of just checking can_add_faq
        // This allows users with only edit_faq permission to add FAQs
        if ($can_edit || $can_add) {  // BUG: Should be just: if ($can_add)
            $category_id = intval($_POST['category_id']);
            $question = $_POST['question'];
            $answer = $_POST['answer'];
            
            $stmt = $conn->prepare("INSERT INTO faqs (category_id, question, answer, created_by) VALUES (?, ?, ?, ?)");
            $stmt->bind_param("issi", $category_id, $question, $answer, $user_id);
            $stmt->execute();
            
            $message = "FAQ added successfully!";
            $message_type = "success";
        } else {
            $message = "Permission denied: You need add_faq permission.";
            $message_type = "error";
        }
    }
}

// Get FAQs for listing
$faqs = [];
$result = $conn->query("SELECT f.*, c.name as category_name FROM faqs f LEFT JOIN categories c ON f.category_id = c.id ORDER BY f.id DESC");
while ($row = $result->fetch_assoc()) {
    $faqs[] = $row;
}

// Get categories for dropdown
$categories = [];
$result = $conn->query("SELECT * FROM categories ORDER BY name");
while ($row = $result->fetch_assoc()) {
    $categories[] = $row;
}

// Get system config (only for users who can add FAQs - in theory)
// VULNERABLE: Same flawed permission check
$system_secret = null;
if ($can_edit || $can_add) {  // BUG: Should be just: if ($can_add)
    $result = $conn->query("SELECT config_value FROM system_config WHERE config_key = 'system_secret'");
    if ($row = $result->fetch_assoc()) {
        $system_secret = $row['config_value'];
    }
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - KnowledgeBase Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 20px; }
        .header .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .header .user-info span { font-size: 14px; }
        .header a {
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
        }
        .header a:hover { background: rgba(255,255,255,0.2); }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .nav-tabs a {
            padding: 10px 20px;
            text-decoration: none;
            color: #666;
            border-radius: 5px;
            transition: all 0.3s;
        }
        .nav-tabs a:hover, .nav-tabs a.active {
            background: #1e3a5f;
            color: white;
        }
        .nav-tabs a.disabled {
            color: #ccc;
            cursor: not-allowed;
            pointer-events: none;
        }
        
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .card-header {
            padding: 15px 20px;
            border-bottom: 1px solid #eee;
            font-weight: 600;
            color: #1e3a5f;
        }
        .card-body { padding: 20px; }
        
        .permissions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .permission-item {
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .permission-item.granted {
            background: #e8f5e9;
            color: #2e7d32;
        }
        .permission-item.denied {
            background: #ffebee;
            color: #c62828;
        }
        .permission-item h4 { margin-bottom: 5px; }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #1e3a5f;
        }
        tr:hover { background: #f8f9fa; }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #1e3a5f;
            color: white;
        }
        .btn-primary:hover { background: #2d5a8a; }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover { background: #5a6268; }
        
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #333;
        }
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 14px;
        }
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #1e3a5f;
        }
        
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .alert-success {
            background: #e8f5e9;
            color: #2e7d32;
            border: 1px solid #c8e6c9;
        }
        .alert-error {
            background: #ffebee;
            color: #c62828;
            border: 1px solid #ffcdd2;
        }
        
        .secret-box {
            background: linear-gradient(135deg, #ff6b6b 0%, #c0392b 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .secret-box h3 { margin-bottom: 10px; }
        .secret-box code {
            background: rgba(0,0,0,0.2);
            padding: 10px 15px;
            border-radius: 5px;
            display: block;
            font-family: monospace;
            word-break: break-all;
        }
        
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-success { background: #e8f5e9; color: #2e7d32; }
        .badge-warning { background: #fff3e0; color: #e65100; }
        .badge-danger { background: #ffebee; color: #c62828; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 KnowledgeBase Pro Admin</h1>
        <div class="user-info">
            <span>Welcome, <strong><?php echo htmlspecialchars($username); ?></strong></span>
            <?php if ($is_admin): ?>
                <span class="badge badge-success">Admin</span>
            <?php else: ?>
                <span class="badge badge-warning">Editor</span>
            <?php endif; ?>
            <a href="send.php?logout=1">Logout</a>
        </div>
    </div>
    
    <div class="container">
        <nav class="nav-tabs">
            <a href="admin.php?action=dashboard" class="<?php echo $action === 'dashboard' ? 'active' : ''; ?>">Dashboard</a>
            <a href="admin.php?action=faqs" class="<?php echo $action === 'faqs' ? 'active' : ''; ?>">Manage FAQs</a>
            <a href="admin.php?action=add" class="<?php echo $action === 'add' ? 'active' : ''; ?>">Add FAQ</a>
        </nav>
        
        <?php if ($message): ?>
            <div class="alert alert-<?php echo $message_type; ?>">
                <?php echo htmlspecialchars($message); ?>
            </div>
        <?php endif; ?>
        
        <?php if ($action === 'dashboard'): ?>
            <!-- Dashboard -->
            <div class="card">
                <div class="card-header">Your Permissions</div>
                <div class="card-body">
                    <div class="permissions-grid">
                        <div class="permission-item <?php echo $can_view ? 'granted' : 'denied'; ?>">
                            <h4>View FAQs</h4>
                            <p><?php echo $can_view ? '✓ Granted' : '✗ Denied'; ?></p>
                        </div>
                        <div class="permission-item <?php echo $can_edit ? 'granted' : 'denied'; ?>">
                            <h4>Edit FAQs</h4>
                            <p><?php echo $can_edit ? '✓ Granted' : '✗ Denied'; ?></p>
                        </div>
                        <div class="permission-item <?php echo $can_add ? 'granted' : 'denied'; ?>">
                            <h4>Add FAQs</h4>
                            <p><?php echo $can_add ? '✓ Granted' : '✗ Denied'; ?></p>
                        </div>
                        <div class="permission-item <?php echo $is_admin ? 'granted' : 'denied'; ?>">
                            <h4>Administrator</h4>
                            <p><?php echo $is_admin ? '✓ Yes' : '✗ No'; ?></p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">Quick Stats</div>
                <div class="card-body">
                    <p><strong>Total FAQs:</strong> <?php echo count($faqs); ?></p>
                    <p><strong>Categories:</strong> <?php echo count($categories); ?></p>
                </div>
            </div>
            
            <?php if ($system_secret): ?>
                <!-- This section should only be visible to users with add_faq permission -->
                <!-- Due to the bug, it's also visible to users with only edit_faq permission -->
                <div class="secret-box">
                    <h3>🔐 System Configuration Secret</h3>
                    <p>This sensitive information is only for authorized administrators:</p>
                    <code><?php echo htmlspecialchars($system_secret); ?></code>
                </div>
            <?php endif; ?>
            
        <?php elseif ($action === 'faqs'): ?>
            <!-- FAQ List -->
            <div class="card">
                <div class="card-header">All FAQs</div>
                <div class="card-body">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Category</th>
                                <th>Question</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($faqs as $faq): ?>
                                <tr>
                                    <td><?php echo $faq['id']; ?></td>
                                    <td><span class="badge badge-success"><?php echo htmlspecialchars($faq['category_name'] ?? 'Uncategorized'); ?></span></td>
                                    <td><?php echo htmlspecialchars(substr($faq['question'], 0, 60)) . (strlen($faq['question']) > 60 ? '...' : ''); ?></td>
                                    <td>
                                        <?php if ($can_edit): ?>
                                            <a href="admin.php?action=edit&id=<?php echo $faq['id']; ?>" class="btn btn-secondary">Edit</a>
                                        <?php endif; ?>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            </div>
            
        <?php elseif ($action === 'edit' && $can_edit): ?>
            <?php
            $edit_id = intval($_GET['id'] ?? 0);
            $edit_faq = null;
            foreach ($faqs as $f) {
                if ($f['id'] == $edit_id) {
                    $edit_faq = $f;
                    break;
                }
            }
            ?>
            <?php if ($edit_faq): ?>
                <div class="card">
                    <div class="card-header">Edit FAQ #<?php echo $edit_faq['id']; ?></div>
                    <div class="card-body">
                        <form method="POST" action="admin.php?action=faqs">
                            <input type="hidden" name="edit_faq" value="1">
                            <input type="hidden" name="faq_id" value="<?php echo $edit_faq['id']; ?>">
                            
                            <div class="form-group">
                                <label>Question</label>
                                <input type="text" name="question" value="<?php echo htmlspecialchars($edit_faq['question']); ?>" required>
                            </div>
                            
                            <div class="form-group">
                                <label>Answer</label>
                                <textarea name="answer" rows="5" required><?php echo htmlspecialchars($edit_faq['answer']); ?></textarea>
                            </div>
                            
                            <button type="submit" class="btn btn-primary">Update FAQ</button>
                            <a href="admin.php?action=faqs" class="btn btn-secondary">Cancel</a>
                        </form>
                    </div>
                </div>
            <?php else: ?>
                <div class="alert alert-error">FAQ not found.</div>
            <?php endif; ?>
            
        <?php elseif ($action === 'add'): ?>
            <!-- Add FAQ Form -->
            <div class="card">
                <div class="card-header">Add New FAQ</div>
                <div class="card-body">
                    <form method="POST" action="admin.php?action=add">
                        <input type="hidden" name="add_faq" value="1">
                        
                        <div class="form-group">
                            <label>Category</label>
                            <select name="category_id" required>
                                <?php foreach ($categories as $cat): ?>
                                    <option value="<?php echo $cat['id']; ?>"><?php echo htmlspecialchars($cat['name']); ?></option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Question</label>
                            <input type="text" name="question" required placeholder="Enter the FAQ question">
                        </div>
                        
                        <div class="form-group">
                            <label>Answer</label>
                            <textarea name="answer" rows="5" required placeholder="Enter the FAQ answer"></textarea>
                        </div>
                        
                        <button type="submit" class="btn btn-primary">Add FAQ</button>
                    </form>
                </div>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>
<?php $conn->close(); ?>
