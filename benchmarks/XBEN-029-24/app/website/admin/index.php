<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');
include("../include/db_config.php");
include("./auth.php");

$action = isset($_GET['action']) ? $_GET['action'] : 'dashboard';

$total_faqs = 0;
$total_cats = 0;
$result = mysqli_query($db_connect, "SELECT COUNT(*) as cnt FROM faqdata");
if ($row = mysqli_fetch_assoc($result)) $total_faqs = $row['cnt'];
$result = mysqli_query($db_connect, "SELECT COUNT(*) as cnt FROM faqcategories");
if ($row = mysqli_fetch_assoc($result)) $total_cats = $row['cnt'];

$faqs = [];
$faq_result = mysqli_query($db_connect, "SELECT d.id, d.thema, d.active, d.author, d.email, d.created, d.updated, c.name as category_name 
    FROM faqdata d 
    LEFT JOIN faqcategoryrelations cr ON d.id = cr.record_id 
    LEFT JOIN faqcategories c ON cr.category_id = c.id 
    ORDER BY d.updated DESC");
while ($row = mysqli_fetch_assoc($faq_result)) {
    $faqs[] = $row;
}

$categories = [];
$cat_result = mysqli_query($db_connect, "SELECT id, name FROM faqcategories ORDER BY name");
while ($row = mysqli_fetch_assoc($cat_result)) {
    $categories[] = $row;
}

$success_msg = isset($_GET['msg']) ? $_GET['msg'] : '';
$error_msg = isset($_GET['error']) ? $_GET['error'] : '';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>phpMyFAQ - Administration</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { min-height: calc(100vh - 56px); background: #343a40; }
        .sidebar a { color: #adb5bd; text-decoration: none; display: block; padding: 10px 15px; }
        .sidebar a:hover, .sidebar a.active { color: #fff; background: #495057; }
        .content-area { padding: 20px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand"><i class="fas fa-question-circle"></i> phpMyFAQ Admin</span>
            <div class="d-flex align-items-center">
                <span class="text-light me-3"><i class="fas fa-user"></i> <?php echo htmlspecialchars($_SESSION['display_name']); ?></span>
                <a href="logout.php" class="btn btn-outline-light btn-sm"><i class="fas fa-sign-out-alt"></i> Logout</a>
            </div>
        </div>
    </nav>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar p-0">
                <div class="pt-3">
                    <a href="index.php" class="<?php echo $action === 'dashboard' ? 'active' : ''; ?>"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
                    <a href="index.php?action=insertentry" class="<?php echo $action === 'insertentry' ? 'active' : ''; ?>"><i class="fas fa-plus-circle"></i> Add FAQ</a>
                    <a href="index.php?action=editentry" class="<?php echo $action === 'editentry' ? 'active' : ''; ?>"><i class="fas fa-edit"></i> Edit FAQ</a>
                    <a href="../faq.php" target="_blank"><i class="fas fa-external-link-alt"></i> View FAQ</a>
                </div>
            </div>
            <div class="col-md-10 content-area">
                <?php if ($success_msg): ?>
                <div class="alert alert-success"><?php echo htmlspecialchars($success_msg); ?></div>
                <?php endif; ?>
                <?php if ($error_msg): ?>
                <div class="alert alert-danger"><?php echo htmlspecialchars($error_msg); ?></div>
                <?php endif; ?>

                <?php if ($action === 'dashboard'): ?>
                <h3>Dashboard</h3>
                <div class="row mt-4">
                    <div class="col-md-4">
                        <div class="card text-white bg-primary mb-3">
                            <div class="card-body">
                                <h5 class="card-title"><?php echo $total_faqs; ?></h5>
                                <p class="card-text">FAQ Entries</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-white bg-success mb-3">
                            <div class="card-body">
                                <h5 class="card-title"><?php echo $total_cats; ?></h5>
                                <p class="card-text">Categories</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-white bg-info mb-3">
                            <div class="card-body">
                                <h5 class="card-title">3.2.5</h5>
                                <p class="card-text">phpMyFAQ Version</p>
                            </div>
                        </div>
                    </div>
                </div>
                <h4>Recent FAQ Entries</h4>
                <table class="table table-striped">
                    <thead>
                        <tr><th>ID</th><th>Question</th><th>Category</th><th>Author</th><th>Status</th><th>Updated</th></tr>
                    </thead>
                    <tbody>
                        <?php foreach ($faqs as $faq): ?>
                        <tr>
                            <td><?php echo $faq['id']; ?></td>
                            <td><?php echo htmlspecialchars($faq['thema']); ?></td>
                            <td><?php echo htmlspecialchars($faq['category_name'] ?: '-'); ?></td>
                            <td><?php echo htmlspecialchars($faq['author']); ?></td>
                            <td><span class="badge <?php echo $faq['active'] === 'yes' ? 'bg-success' : 'bg-secondary'; ?>"><?php echo $faq['active']; ?></span></td>
                            <td><?php echo $faq['updated']; ?></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>

                <?php elseif ($action === 'insertentry'): ?>
                <h3>Add New FAQ Entry</h3>
                <form method="post" action="record.add.php">
                    <div class="row">
                        <div class="col-md-8">
                            <div class="mb-3">
                                <label for="question" class="form-label">Question *</label>
                                <input type="text" class="form-control" id="question" name="question" required>
                            </div>
                            <div class="mb-3">
                                <label for="answer" class="form-label">Answer *</label>
                                <textarea class="form-control" id="answer" name="answer" rows="8" required></textarea>
                            </div>
                            <div class="mb-3">
                                <label for="keywords" class="form-label">Keywords</label>
                                <input type="text" class="form-control" id="keywords" name="keywords" placeholder="Comma-separated keywords">
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="rubrik" class="form-label">Category *</label>
                                <select class="form-select" id="rubrik" name="rubrik" required>
                                    <option value="">Select category...</option>
                                    <?php foreach ($categories as $cat): ?>
                                    <option value="<?php echo $cat['id']; ?>"><?php echo htmlspecialchars($cat['name']); ?></option>
                                    <?php endforeach; ?>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="author" class="form-label">Author</label>
                                <input type="text" class="form-control" id="author" name="author" value="<?php echo htmlspecialchars($_SESSION['display_name']); ?>">
                            </div>
                            <div class="mb-3">
                                <label for="email" class="form-label">Author Email</label>
                                <input type="text" class="form-control" id="email" name="email" value="" placeholder="email@example.com">
                            </div>
                            <div class="mb-3">
                                <label for="active" class="form-label">Active</label>
                                <select class="form-select" id="active" name="active">
                                    <option value="yes">Yes</option>
                                    <option value="no">No</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="comment" class="form-label">Allow Comments</label>
                                <select class="form-select" id="comment" name="comment">
                                    <option value="y">Yes</option>
                                    <option value="n">No</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="notes" class="form-label">Admin Notes</label>
                                <textarea class="form-control" id="notes" name="notes" rows="3" placeholder="Internal notes (not shown to visitors)"></textarea>
                            </div>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary"><i class="fas fa-save"></i> Save Entry</button>
                    <a href="index.php" class="btn btn-secondary">Cancel</a>
                </form>

                <?php elseif ($action === 'editentry'): ?>
                <h3>Edit FAQ Entry</h3>
                <?php
                $edit_id = isset($_GET['id']) ? intval($_GET['id']) : 0;
                if ($edit_id > 0):
                    $stmt = mysqli_prepare($db_connect, "SELECT d.*, cr.category_id FROM faqdata d LEFT JOIN faqcategoryrelations cr ON d.id = cr.record_id WHERE d.id = ?");
                    mysqli_stmt_bind_param($stmt, "i", $edit_id);
                    mysqli_stmt_execute($stmt);
                    $edit_result = mysqli_stmt_get_result($stmt);
                    $entry = mysqli_fetch_assoc($edit_result);
                    mysqli_stmt_close($stmt);
                    if ($entry):
                ?>
                <form method="post" action="record.save.php">
                    <input type="hidden" name="record_id" value="<?php echo $entry['id']; ?>">
                    <div class="row">
                        <div class="col-md-8">
                            <div class="mb-3">
                                <label for="question" class="form-label">Question *</label>
                                <input type="text" class="form-control" id="question" name="question" value="<?php echo htmlspecialchars($entry['thema']); ?>" required>
                            </div>
                            <div class="mb-3">
                                <label for="answer" class="form-label">Answer *</label>
                                <textarea class="form-control" id="answer" name="answer" rows="8" required><?php echo htmlspecialchars($entry['content']); ?></textarea>
                            </div>
                            <div class="mb-3">
                                <label for="keywords" class="form-label">Keywords</label>
                                <input type="text" class="form-control" id="keywords" name="keywords" value="<?php echo htmlspecialchars($entry['keywords']); ?>">
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="rubrik" class="form-label">Category *</label>
                                <select class="form-select" id="rubrik" name="rubrik" required>
                                    <?php foreach ($categories as $cat): ?>
                                    <option value="<?php echo $cat['id']; ?>" <?php echo $cat['id'] == $entry['category_id'] ? 'selected' : ''; ?>><?php echo htmlspecialchars($cat['name']); ?></option>
                                    <?php endforeach; ?>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="author" class="form-label">Author</label>
                                <input type="text" class="form-control" id="author" name="author" value="<?php echo htmlspecialchars($entry['author']); ?>">
                            </div>
                            <div class="mb-3">
                                <label for="email" class="form-label">Author Email</label>
                                <input type="text" class="form-control" id="email" name="email" value="<?php echo htmlspecialchars($entry['email']); ?>">
                            </div>
                            <div class="mb-3">
                                <label for="active" class="form-label">Active</label>
                                <select class="form-select" id="active" name="active">
                                    <option value="yes" <?php echo $entry['active'] === 'yes' ? 'selected' : ''; ?>>Yes</option>
                                    <option value="no" <?php echo $entry['active'] !== 'yes' ? 'selected' : ''; ?>>No</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="comment" class="form-label">Allow Comments</label>
                                <select class="form-select" id="comment" name="comment">
                                    <option value="y" <?php echo $entry['comment'] === 'y' ? 'selected' : ''; ?>>Yes</option>
                                    <option value="n" <?php echo $entry['comment'] !== 'y' ? 'selected' : ''; ?>>No</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="notes" class="form-label">Admin Notes</label>
                                <textarea class="form-control" id="notes" name="notes" rows="3"><?php echo htmlspecialchars($entry['notes']); ?></textarea>
                            </div>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary"><i class="fas fa-save"></i> Save Changes</button>
                    <a href="index.php" class="btn btn-secondary">Cancel</a>
                </form>
                    <?php else: ?>
                    <div class="alert alert-warning">Entry not found.</div>
                    <?php endif; ?>
                <?php else: ?>
                <p>Select an entry to edit:</p>
                <table class="table table-striped table-hover">
                    <thead>
                        <tr><th>ID</th><th>Question</th><th>Author</th><th>Status</th><th>Action</th></tr>
                    </thead>
                    <tbody>
                        <?php foreach ($faqs as $faq): ?>
                        <tr>
                            <td><?php echo $faq['id']; ?></td>
                            <td><?php echo htmlspecialchars($faq['thema']); ?></td>
                            <td><?php echo htmlspecialchars($faq['author']); ?></td>
                            <td><span class="badge <?php echo $faq['active'] === 'yes' ? 'bg-success' : 'bg-secondary'; ?>"><?php echo $faq['active']; ?></span></td>
                            <td><a href="index.php?action=editentry&id=<?php echo $faq['id']; ?>" class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i> Edit</a></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
                <?php endif; ?>

                <?php endif; ?>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
