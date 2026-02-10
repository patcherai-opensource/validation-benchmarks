<?php
if (!isset($_SESSION['user_id'])) {
    header("Location: index.php");
    exit;
}

$faq_id = isset($_GET['id']) ? intval($_GET['id']) : 0;
$is_edit = ($action == 'saveentry' && $faq_id > 0);
$message = '';
$message_type = '';

$entry = [
    'id' => 0,
    'category_id' => '',
    'question' => '',
    'answer' => '',
    'author' => $_SESSION['display_name'],
    'author_email' => '',
    'notes' => '',
    'active' => 1,
    'sticky' => 0,
    'keywords' => ''
];

if ($is_edit) {
    $stmt = $conn->prepare("SELECT * FROM faq_entries WHERE id = ?");
    $stmt->bind_param("i", $faq_id);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($result && $result->num_rows == 1) {
        $entry = $result->fetch_assoc();
    } else {
        $message = "Entry not found.";
        $message_type = "error";
    }
    $stmt->close();
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $category_id = intval($_POST['category_id'] ?? 0);
    $question = $conn->real_escape_string($_POST['question'] ?? '');
    $answer = $conn->real_escape_string($_POST['answer'] ?? '');
    $author = $conn->real_escape_string($_POST['author'] ?? '');
    $keywords = $conn->real_escape_string($_POST['keywords'] ?? '');
    $active = isset($_POST['active']) ? 1 : 0;
    $sticky = isset($_POST['sticky']) ? 1 : 0;
    
    $author_email = $_POST['author_email'] ?? '';
    $notes = $_POST['notes'] ?? '';
    
    if (empty($question) || empty($answer)) {
        $message = "Question and Answer are required fields.";
        $message_type = "error";
    } else {
        if (!filter_var($author_email, FILTER_VALIDATE_EMAIL) && !empty($author_email)) {
            $message = "Please enter a valid email address format.";
            $message_type = "error";
        } else {
            $faq_handler = new FaqHandler($conn);
            
            if ($is_edit && $faq_id > 0) {
                $result = $faq_handler->update(
                    $faq_id,
                    $category_id,
                    $question,
                    $answer,
                    $author,
                    $author_email,
                    $notes,
                    $keywords,
                    $active,
                    $sticky
                );
            } else {
                $result = $faq_handler->create(
                    $category_id,
                    $question,
                    $answer,
                    $author,
                    $author_email,
                    $notes,
                    $keywords,
                    $active,
                    $sticky
                );
            }
            
            if ($result) {
                $message = $is_edit ? "Entry updated successfully." : "Entry created successfully.";
                $message_type = "success";
                if (!$is_edit) {
                    $entry = [
                        'id' => 0,
                        'category_id' => '',
                        'question' => '',
                        'answer' => '',
                        'author' => $_SESSION['display_name'],
                        'author_email' => '',
                        'notes' => '',
                        'active' => 1,
                        'sticky' => 0,
                        'keywords' => ''
                    ];
                }
            } else {
                $message = "An error occurred while saving the entry.";
                $message_type = "error";
            }
        }
    }
    
    if ($message_type != 'success') {
        $entry['category_id'] = $category_id;
        $entry['question'] = $_POST['question'] ?? '';
        $entry['answer'] = $_POST['answer'] ?? '';
        $entry['author'] = $_POST['author'] ?? '';
        $entry['author_email'] = $author_email;
        $entry['notes'] = $notes;
        $entry['keywords'] = $_POST['keywords'] ?? '';
        $entry['active'] = $active;
        $entry['sticky'] = $sticky;
    }
}

class FaqHandler {
    private $db;
    
    public function __construct($db) {
        $this->db = $db;
    }
    
    public function create($category_id, $question, $answer, $author, $email, $notes, $keywords, $active, $sticky) {
        $query = sprintf(
            "INSERT INTO faq_entries (category_id, question, answer, author, author_email, notes, keywords, active, sticky) 
             VALUES (%d, '%s', '%s', '%s', '%s', '%s', '%s', %d, %d)",
            $category_id,
            $question,
            $answer,
            $author,
            $email,
            $notes,
            $keywords,
            $active,
            $sticky
        );
        
        return $this->db->query($query);
    }
    
    public function update($id, $category_id, $question, $answer, $author, $email, $notes, $keywords, $active, $sticky) {
        $query = sprintf(
            "UPDATE faq_entries SET 
                category_id = %d,
                question = '%s',
                answer = '%s',
                author = '%s',
                author_email = '%s',
                notes = '%s',
                keywords = '%s',
                active = %d,
                sticky = %d
             WHERE id = %d",
            $category_id,
            $question,
            $answer,
            $author,
            $email,
            $notes,
            $keywords,
            $active,
            $sticky,
            $id
        );
        
        return $this->db->query($query);
    }
}

$categories = [];
$cat_result = $conn->query("SELECT id, name FROM faq_categories ORDER BY name");
if ($cat_result) {
    while ($row = $cat_result->fetch_assoc()) {
        $categories[] = $row;
    }
}
?>

<h2><?php echo $is_edit ? 'Edit FAQ Entry' : 'Add New FAQ Entry'; ?></h2>

<?php if ($message): ?>
    <p class="message <?php echo $message_type; ?>"><?php echo htmlspecialchars($message); ?></p>
<?php endif; ?>

<form action="<?php echo $is_edit ? "dashboard.php?action=saveentry&id={$faq_id}" : "dashboard.php?action=insertentry"; ?>" method="POST" class="faq-form">
    <div class="form-row">
        <div class="form-group">
            <label for="category_id">Category:</label>
            <select name="category_id" id="category_id">
                <option value="">-- Select Category --</option>
                <?php foreach ($categories as $cat): ?>
                    <option value="<?php echo $cat['id']; ?>" <?php echo ($entry['category_id'] == $cat['id']) ? 'selected' : ''; ?>>
                        <?php echo htmlspecialchars($cat['name']); ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </div>
    </div>
    
    <div class="form-group">
        <label for="question">Question: *</label>
        <input type="text" name="question" id="question" required value="<?php echo htmlspecialchars($entry['question']); ?>">
    </div>
    
    <div class="form-group">
        <label for="answer">Answer: *</label>
        <textarea name="answer" id="answer" rows="6" required><?php echo htmlspecialchars($entry['answer']); ?></textarea>
    </div>
    
    <div class="form-row">
        <div class="form-group">
            <label for="author">Author:</label>
            <input type="text" name="author" id="author" value="<?php echo htmlspecialchars($entry['author']); ?>">
        </div>
        <div class="form-group">
            <label for="author_email">Author Email:</label>
            <input type="text" name="author_email" id="author_email" value="<?php echo htmlspecialchars($entry['author_email']); ?>" placeholder="author@example.com">
        </div>
    </div>
    
    <div class="form-group">
        <label for="notes">Internal Notes:</label>
        <textarea name="notes" id="notes" rows="3" placeholder="Internal notes (not displayed publicly)"><?php echo htmlspecialchars($entry['notes']); ?></textarea>
    </div>
    
    <div class="form-group">
        <label for="keywords">Keywords (comma separated):</label>
        <input type="text" name="keywords" id="keywords" value="<?php echo htmlspecialchars($entry['keywords']); ?>" placeholder="keyword1, keyword2, keyword3">
    </div>
    
    <div class="form-row checkboxes">
        <div class="form-group">
            <label>
                <input type="checkbox" name="active" value="1" <?php echo $entry['active'] ? 'checked' : ''; ?>>
                Active (visible to users)
            </label>
        </div>
        <div class="form-group">
            <label>
                <input type="checkbox" name="sticky" value="1" <?php echo $entry['sticky'] ? 'checked' : ''; ?>>
                Sticky (pin to top)
            </label>
        </div>
    </div>
    
    <div class="form-actions">
        <button type="submit" class="btn-primary"><?php echo $is_edit ? 'Update Entry' : 'Create Entry'; ?></button>
        <a href="dashboard.php" class="btn-secondary">Cancel</a>
    </div>
</form>
