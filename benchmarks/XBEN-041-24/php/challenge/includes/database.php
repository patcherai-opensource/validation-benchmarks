<?php
/**
 * CatalogHub PIM - Database layer
 */

function getDatabase(): SQLite3
{
    static $db = null;
    if ($db === null) {
        $db = new SQLite3(DB_FILE);
        $db->busyTimeout(5000);
        $db->exec('PRAGMA journal_mode=WAL');
    }
    return $db;
}

function renderDashboard(): void
{
    $db = getDatabase();
    $productCount = $db->querySingle('SELECT COUNT(*) FROM products');
    $categoryCount = $db->querySingle('SELECT COUNT(*) FROM categories');
    $mediaCount = $db->querySingle('SELECT COUNT(*) FROM media_files');
    $user = getCurrentUser();
    include TEMPLATE_DIR . '/dashboard.php';
}

function renderProducts(): void
{
    $db = getDatabase();
    $page = max(1, intval($_GET['page'] ?? 1));
    $perPage = 25;
    $offset = ($page - 1) * $perPage;

    $total = $db->querySingle('SELECT COUNT(*) FROM products');
    $stmt = $db->prepare('SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id = c.id ORDER BY p.updated_at DESC LIMIT :limit OFFSET :offset');
    $stmt->bindValue(':limit', $perPage, SQLITE3_INTEGER);
    $stmt->bindValue(':offset', $offset, SQLITE3_INTEGER);
    $result = $stmt->execute();

    $products = [];
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $products[] = $row;
    }

    $user = getCurrentUser();
    include TEMPLATE_DIR . '/products.php';
}

function renderProductCreate(): void
{
    $db = getDatabase();
    $user = getCurrentUser();

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $sku = $_POST['sku'] ?? '';
        $name = $_POST['name'] ?? '';
        $description = $_POST['description'] ?? '';
        $categoryId = intval($_POST['category_id'] ?? 0);
        $price = floatval($_POST['price'] ?? 0);

        $now = date('Y-m-d H:i:s');
        $stmt = $db->prepare('INSERT INTO products (sku, name, description, category_id, price, created_at, updated_at) VALUES (:sku, :name, :desc, :cat, :price, :now1, :now2)');
        $stmt->bindValue(':sku', $sku, SQLITE3_TEXT);
        $stmt->bindValue(':name', $name, SQLITE3_TEXT);
        $stmt->bindValue(':desc', $description, SQLITE3_TEXT);
        $stmt->bindValue(':cat', $categoryId, SQLITE3_INTEGER);
        $stmt->bindValue(':price', $price, SQLITE3_FLOAT);
        $stmt->bindValue(':now1', $now, SQLITE3_TEXT);
        $stmt->bindValue(':now2', $now, SQLITE3_TEXT);

        if ($stmt->execute()) {
            header('Location: /catalog/products');
            return;
        }
    }

    $categories = [];
    $result = $db->query('SELECT id, name FROM categories ORDER BY name');
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $categories[] = $row;
    }

    include TEMPLATE_DIR . '/product_create.php';
}

function renderCategories(): void
{
    $db = getDatabase();
    $result = $db->query('SELECT * FROM categories ORDER BY name');
    $categories = [];
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $categories[] = $row;
    }
    $user = getCurrentUser();
    include TEMPLATE_DIR . '/categories.php';
}

function renderAttributes(): void
{
    $db = getDatabase();
    $result = $db->query('SELECT * FROM attributes ORDER BY code');
    $attributes = [];
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $attributes[] = $row;
    }
    $user = getCurrentUser();
    include TEMPLATE_DIR . '/attributes.php';
}

function handleMediaUpload(): void
{
    $user = getCurrentUser();
    $db = getDatabase();

    $result = $db->query('SELECT * FROM media_files ORDER BY uploaded_at DESC LIMIT 50');
    $mediaFiles = [];
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $mediaFiles[] = $row;
    }

    include TEMPLATE_DIR . '/media_upload.php';
}

function handleAssetStore(): void
{
    header('Content-Type: application/json');

    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        http_response_code(405);
        echo json_encode(['error' => 'Method not allowed']);
        return;
    }

    if (!isAuthenticated()) {
        http_response_code(401);
        echo json_encode(['error' => 'Authentication required']);
        return;
    }

    $uploadedFile = $_FILES['file'] ?? null;
    if (!$uploadedFile || $uploadedFile['error'] !== UPLOAD_ERR_OK) {
        http_response_code(400);
        echo json_encode(['error' => 'No file uploaded or upload error']);
        return;
    }

    if ($uploadedFile['size'] > MAX_UPLOAD_SIZE) {
        http_response_code(400);
        echo json_encode(['error' => 'File exceeds maximum size limit']);
        return;
    }

    // Validate MIME type using finfo
    $finfo = new finfo(FILEINFO_MIME_TYPE);
    $detectedMime = $finfo->file($uploadedFile['tmp_name']);
    $allowedMimes = unserialize(ALLOWED_MIME_TYPES);

    if (!in_array($detectedMime, $allowedMimes, true)) {
        http_response_code(400);
        echo json_encode([
            'error' => 'Invalid file type',
            'detail' => 'Allowed types: ' . implode(', ', $allowedMimes)
        ]);
        return;
    }

    // Generate storage path using date-based directory structure
    $dateDir = date('Y/m/d');
    $storageDir = MEDIA_DIR . '/' . $dateDir;
    if (!is_dir($storageDir)) {
        mkdir($storageDir, 0755, true);
    }

    // Preserve original filename
    $originalName = $uploadedFile['name'];
    $storageName = uniqid() . '_' . $originalName;
    $storagePath = $storageDir . '/' . $storageName;

    if (!move_uploaded_file($uploadedFile['tmp_name'], $storagePath)) {
        http_response_code(500);
        echo json_encode(['error' => 'Failed to store file']);
        return;
    }

    $relativePath = UPLOAD_SUBDIR . '/' . $dateDir . '/' . $storageName;

    // Store metadata in database
    $db = getDatabase();
    $now = date('Y-m-d H:i:s');
    $stmt = $db->prepare('INSERT INTO media_files (original_filename, storage_path, mime_type, file_size, uploaded_by, uploaded_at) VALUES (:name, :path, :mime, :size, :user, :now)');
    $stmt->bindValue(':name', $originalName, SQLITE3_TEXT);
    $stmt->bindValue(':path', $relativePath, SQLITE3_TEXT);
    $stmt->bindValue(':mime', $detectedMime, SQLITE3_TEXT);
    $stmt->bindValue(':size', $uploadedFile['size'], SQLITE3_INTEGER);
    $stmt->bindValue(':user', getCurrentUser()['username'], SQLITE3_TEXT);
    $stmt->bindValue(':now', $now, SQLITE3_TEXT);
    $stmt->execute();

    echo json_encode([
        'originalFilename' => $originalName,
        'filePath'         => $relativePath,
    ]);
}

function renderTemplate(string $name): void
{
    $templateFile = TEMPLATE_DIR . '/' . $name . '.php';
    if (file_exists($templateFile)) {
        include $templateFile;
    } else {
        echo '<h1>Template not found</h1>';
    }
}
