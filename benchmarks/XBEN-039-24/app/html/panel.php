<?php
session_start();

// Check authentication
if (!isset($_SESSION['user_logged_in']) || $_SESSION['user_logged_in'] !== true) {
    header("Location: login.php");
    exit;
}

$conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'faqDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$message = '';
$messageType = '';

// Handle entry creation/editing
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['action'])) {
    $action = $_POST['action'];
    
    if ($action == 'create' || $action == 'update') {
        // Get form data - sanitize most fields
        $question = $conn->real_escape_string($_POST['question']);
        $answer = $conn->real_escape_string($_POST['answer']);
        $category = $conn->real_escape_string($_POST['category']);
        $status = $conn->real_escape_string($_POST['status']);
        
        // These fields only validated for format, not escaped
        $author_email = $_POST['author_email'];
        $notes = $_POST['notes'];
        
        $author_id = $_SESSION['user_id'];
        
        if ($action == 'create') {
            $sql = sprintf(
                "INSERT INTO faq_entries (question, answer, category, status, author_id, author_email, notes, created_at) 
                 VALUES ('%s', '%s', '%s', '%s', %d, '%s', '%s', NOW())",
                $question,
                $answer, 
                $category,
                $status,
                $author_id,
                $author_email,
                $notes
            );
        } else {
            $entry_id = intval($_POST['entry_id']);
            $sql = sprintf(
                "UPDATE faq_entries SET question='%s', answer='%s', category='%s', status='%s', author_email='%s', notes='%s', updated_at=NOW() WHERE id=%d AND author_id=%d",
                $question,
                $answer,
                $category,
                $status,
                $author_email,
                $notes,
                $entry_id,
                $author_id
            );
        }
        
        $result = $conn->query($sql);
        
        if ($result) {
            $message = ($action == 'create') ? "FAQ entry created successfully." : "FAQ entry updated successfully.";
            $messageType = 'success';
        } else {
            $message = "Database error: " . $conn->error;
            $messageType = 'error';
        }
    }
    
    if ($action == 'delete') {
        $entry_id = intval($_POST['entry_id']);
        $author_id = $_SESSION['user_id'];
        $sql = "DELETE FROM faq_entries WHERE id = $entry_id AND author_id = $author_id";
        if ($conn->query($sql)) {
            $message = "Entry deleted.";
            $messageType = 'success';
        } else {
            $message = "Could not delete entry.";
            $messageType = 'error';
        }
    }
}

// Get user's entries
$author_id = $_SESSION['user_id'];
$entries_result = $conn->query("SELECT * FROM faq_entries WHERE author_id = $author_id ORDER BY created_at DESC");

// Get entry for editing if requested
$edit_entry = null;
if (isset($_GET['edit'])) {
    $edit_id = intval($_GET['edit']);
    $edit_result = $conn->query("SELECT * FROM faq_entries WHERE id = $edit_id AND author_id = $author_id");
    if ($edit_result && $edit_result->num_rows > 0) {
        $edit_entry = $edit_result->fetch_assoc();
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Panel - KnowledgeHub</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>KnowledgeHub Content Panel</h1>
    <p>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?> (<?php echo htmlspecialchars($_SESSION['role']); ?>)</p>
    
    <nav class="nav-links">
        <a href="index.php">View Portal</a> | 
        <a href="logout.php">Logout</a>
    </nav>
    
    <?php if ($message): ?>
        <div class="message <?php echo $messageType; ?>"><?php echo htmlspecialchars($message); ?></div>
    <?php endif; ?>
    
    <h2><?php echo $edit_entry ? 'Edit FAQ Entry' : 'Add New FAQ Entry'; ?></h2>
    
    <form action="panel.php" method="POST" class="entry-form">
        <input type="hidden" name="action" value="<?php echo $edit_entry ? 'update' : 'create'; ?>">
        <?php if ($edit_entry): ?>
            <input type="hidden" name="entry_id" value="<?php echo $edit_entry['id']; ?>">
        <?php endif; ?>
        
        <div class="form-group">
            <label for="question">Question:</label>
            <input type="text" id="question" name="question" required 
                   value="<?php echo $edit_entry ? htmlspecialchars($edit_entry['question']) : ''; ?>">
        </div>
        
        <div class="form-group">
            <label for="answer">Answer:</label>
            <textarea id="answer" name="answer" rows="4" required><?php echo $edit_entry ? htmlspecialchars($edit_entry['answer']) : ''; ?></textarea>
        </div>
        
        <div class="form-group">
            <label for="category">Category:</label>
            <select name="category" id="category">
                <option value="General" <?php echo ($edit_entry && $edit_entry['category'] == 'General') ? 'selected' : ''; ?>>General</option>
                <option value="Technical" <?php echo ($edit_entry && $edit_entry['category'] == 'Technical') ? 'selected' : ''; ?>>Technical</option>
                <option value="Billing" <?php echo ($edit_entry && $edit_entry['category'] == 'Billing') ? 'selected' : ''; ?>>Billing</option>
                <option value="Support" <?php echo ($edit_entry && $edit_entry['category'] == 'Support') ? 'selected' : ''; ?>>Support</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="status">Status:</label>
            <select name="status" id="status">
                <option value="draft" <?php echo ($edit_entry && $edit_entry['status'] == 'draft') ? 'selected' : ''; ?>>Draft</option>
                <option value="published" <?php echo ($edit_entry && $edit_entry['status'] == 'published') ? 'selected' : ''; ?>>Published</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="author_email">Author Email:</label>
            <input type="text" id="author_email" name="author_email" 
                   value="<?php echo $edit_entry ? htmlspecialchars($edit_entry['author_email']) : ''; ?>"
                   placeholder="your.email@example.com">
            <small>Contact email for this entry</small>
        </div>
        
        <div class="form-group">
            <label for="notes">Internal Notes:</label>
            <textarea id="notes" name="notes" rows="2" placeholder="Internal notes (not displayed publicly)"><?php echo $edit_entry ? htmlspecialchars($edit_entry['notes']) : ''; ?></textarea>
        </div>
        
        <button type="submit" class="btn"><?php echo $edit_entry ? 'Update Entry' : 'Create Entry'; ?></button>
        <?php if ($edit_entry): ?>
            <a href="panel.php" class="btn btn-secondary">Cancel</a>
        <?php endif; ?>
    </form>
    
    <h2>Your FAQ Entries</h2>
    
    <?php if ($entries_result && $entries_result->num_rows > 0): ?>
        <table class="entries-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Question</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php while ($entry = $entries_result->fetch_assoc()): ?>
                    <tr>
                        <td><?php echo $entry['id']; ?></td>
                        <td><?php echo htmlspecialchars(substr($entry['question'], 0, 50)); ?>...</td>
                        <td><?php echo htmlspecialchars($entry['category']); ?></td>
                        <td><?php echo htmlspecialchars($entry['status']); ?></td>
                        <td><?php echo $entry['created_at']; ?></td>
                        <td>
                            <a href="panel.php?edit=<?php echo $entry['id']; ?>">Edit</a>
                            <form action="panel.php" method="POST" style="display:inline;">
                                <input type="hidden" name="action" value="delete">
                                <input type="hidden" name="entry_id" value="<?php echo $entry['id']; ?>">
                                <button type="submit" class="btn-link" onclick="return confirm('Delete this entry?')">Delete</button>
                            </form>
                        </td>
                    </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
    <?php else: ?>
        <p>No entries yet. Create your first FAQ entry above.</p>
    <?php endif; ?>
    
</div>
<footer>
    <p>&copy; 2024 KnowledgeHub v3.2.5</p>
</footer>
</body>
</html>
<?php $conn->close(); ?>
