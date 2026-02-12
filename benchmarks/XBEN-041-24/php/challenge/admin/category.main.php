<?php
/**
 * phpMyFAQ Admin - Category Management
 * Handles category CRUD operations and image uploads
 */

require_once '/var/www/html/src/Session.php';
require_once '/var/www/html/src/Category.php';
require_once '/var/www/html/src/CategoryImage.php';

use phpMyFAQ\Session;
use phpMyFAQ\Category\Category;
use phpMyFAQ\Category\CategoryImage;

Session::init();

if (!Session::isAuthenticated()) {
    header('Location: /admin/');
    exit;
}

$category = new Category();
$categoryImage = new CategoryImage();
$message = '';
$messageType = '';

// Handle form submissions
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';

    switch ($action) {
        case 'add':
            $name = trim($_POST['name'] ?? '');
            $description = trim($_POST['description'] ?? '');
            $lang = $_POST['lang'] ?? 'en';

            if (empty($name)) {
                $message = 'Category name is required.';
                $messageType = 'error';
                break;
            }

            $categoryId = $category->add($name, $description, $lang);

            if ($categoryId && isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK) {
                $categoryImage->setUploadedFile($_FILES['image']);
                $result = $categoryImage->upload($categoryId, $lang);
                if ($result['success']) {
                    $message = 'Category added with image successfully.';
                    $messageType = 'success';
                } else {
                    $message = 'Category added but image upload failed: ' . $result['message'];
                    $messageType = 'warning';
                }
            } else {
                $message = 'Category added successfully.';
                $messageType = 'success';
            }
            break;

        case 'update':
            $id = intval($_POST['id'] ?? 0);
            $name = trim($_POST['name'] ?? '');
            $description = trim($_POST['description'] ?? '');
            $lang = $_POST['lang'] ?? 'en';

            if ($id <= 0 || empty($name)) {
                $message = 'Invalid category data.';
                $messageType = 'error';
                break;
            }

            $category->update($id, $name, $description, $lang);

            if (isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK) {
                $categoryImage->setUploadedFile($_FILES['image']);
                $result = $categoryImage->upload($id, $lang);
                if ($result['success']) {
                    $message = 'Category updated with new image.';
                    $messageType = 'success';
                } else {
                    $message = 'Category updated but image upload failed: ' . $result['message'];
                    $messageType = 'warning';
                }
            } else {
                $message = 'Category updated successfully.';
                $messageType = 'success';
            }
            break;

        case 'delete':
            $id = intval($_POST['id'] ?? 0);
            if ($id > 0) {
                $cat = $category->getById($id);
                if ($cat) {
                    $categoryImage->delete($id, $cat['lang']);
                    $category->delete($id);
                    $message = 'Category deleted.';
                    $messageType = 'success';
                }
            }
            break;
    }
}

$categories = $category->getAll();
$editCategory = null;
if (isset($_GET['edit'])) {
    $editCategory = $category->getById(intval($_GET['edit']));
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>phpMyFAQ Admin - Categories</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <header class="admin-header">
        <div class="container">
            <h1><a href="/admin/">phpMyFAQ Admin</a></h1>
            <nav>
                <a href="/admin/">Dashboard</a>
                <a href="/admin/category.main.php" class="active">Categories</a>
                <a href="/admin/user.php">Users</a>
                <a href="/admin/config.php">Configuration</a>
                <a href="/admin/?action=logout">Logout (<?= htmlspecialchars(Session::getUser()) ?>)</a>
            </nav>
        </div>
    </header>

    <main class="container admin-main">
        <h2>Category Management</h2>

        <?php if ($message): ?>
            <div class="alert alert-<?= $messageType ?>"><?= htmlspecialchars($message) ?></div>
        <?php endif; ?>

        <div class="admin-content">
            <div class="form-section">
                <h3><?= $editCategory ? 'Edit Category' : 'Add New Category' ?></h3>
                <form method="POST" enctype="multipart/form-data" action="/admin/category.main.php">
                    <input type="hidden" name="action" value="<?= $editCategory ? 'update' : 'add' ?>">
                    <?php if ($editCategory): ?>
                        <input type="hidden" name="id" value="<?= $editCategory['id'] ?>">
                    <?php endif; ?>

                    <div class="form-group">
                        <label for="name">Category Name:</label>
                        <input type="text" id="name" name="name" required
                               value="<?= $editCategory ? htmlspecialchars($editCategory['name']) : '' ?>">
                    </div>

                    <div class="form-group">
                        <label for="description">Description:</label>
                        <textarea id="description" name="description" rows="3"><?= $editCategory ? htmlspecialchars($editCategory['description']) : '' ?></textarea>
                    </div>

                    <div class="form-group">
                        <label for="lang">Language:</label>
                        <select id="lang" name="lang">
                            <option value="en" <?= ($editCategory && $editCategory['lang'] === 'en') ? 'selected' : '' ?>>English</option>
                            <option value="de" <?= ($editCategory && $editCategory['lang'] === 'de') ? 'selected' : '' ?>>German</option>
                            <option value="fr" <?= ($editCategory && $editCategory['lang'] === 'fr') ? 'selected' : '' ?>>French</option>
                            <option value="es" <?= ($editCategory && $editCategory['lang'] === 'es') ? 'selected' : '' ?>>Spanish</option>
                            <option value="it" <?= ($editCategory && $editCategory['lang'] === 'it') ? 'selected' : '' ?>>Italian</option>
                            <option value="pt" <?= ($editCategory && $editCategory['lang'] === 'pt') ? 'selected' : '' ?>>Portuguese</option>
                            <option value="nl" <?= ($editCategory && $editCategory['lang'] === 'nl') ? 'selected' : '' ?>>Dutch</option>
                            <option value="ja" <?= ($editCategory && $editCategory['lang'] === 'ja') ? 'selected' : '' ?>>Japanese</option>
                            <option value="zh" <?= ($editCategory && $editCategory['lang'] === 'zh') ? 'selected' : '' ?>>Chinese</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="image">Category Image:</label>
                        <input type="file" id="image" name="image" accept="image/*">
                        <small>Allowed formats: JPG, PNG, GIF, WebP, SVG (max 2MB)</small>
                    </div>

                    <button type="submit" class="btn btn-primary"><?= $editCategory ? 'Update Category' : 'Add Category' ?></button>
                    <?php if ($editCategory): ?>
                        <a href="/admin/category.main.php" class="btn">Cancel</a>
                    <?php endif; ?>
                </form>
            </div>

            <div class="list-section">
                <h3>Existing Categories</h3>
                <?php if (empty($categories)): ?>
                    <p class="empty">No categories found.</p>
                <?php else: ?>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Language</th>
                                <th>Image</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($categories as $cat): ?>
                                <tr>
                                    <td><?= $cat['id'] ?></td>
                                    <td><?= htmlspecialchars($cat['name']) ?></td>
                                    <td><?= htmlspecialchars($cat['lang']) ?></td>
                                    <td>
                                        <?php
                                        $imgUrl = $categoryImage->getImageUrl($cat['id'], $cat['lang']);
                                        if ($imgUrl):
                                        ?>
                                            <img src="<?= htmlspecialchars($imgUrl) ?>" alt="" class="thumb">
                                        <?php else: ?>
                                            <span class="no-image">No image</span>
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <a href="/admin/category.main.php?edit=<?= $cat['id'] ?>" class="btn btn-sm">Edit</a>
                                        <form method="POST" action="/admin/category.main.php" style="display:inline;">
                                            <input type="hidden" name="action" value="delete">
                                            <input type="hidden" name="id" value="<?= $cat['id'] ?>">
                                            <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Delete this category?')">Delete</button>
                                        </form>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                <?php endif; ?>
            </div>
        </div>
    </main>
    <footer>
        <div class="container">
            <p>&copy; 2024 phpMyFAQ Team. Administration Panel</p>
        </div>
    </footer>
</body>
</html>
