<?php
/**
 * CatalogHub PIM - Authentication
 */

function isAuthenticated(): bool
{
    return isset($_SESSION['user_id']) && isset($_SESSION['username']);
}

function getCurrentUser(): ?array
{
    if (!isAuthenticated()) {
        return null;
    }
    return [
        'id'       => $_SESSION['user_id'],
        'username' => $_SESSION['username'],
        'role'     => $_SESSION['role'] ?? 'contributor',
    ];
}

function handleLogin(): void
{
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $username = $_POST['_username'] ?? '';
        $password = $_POST['_password'] ?? '';
        $csrfToken = $_POST['_csrf_token'] ?? '';

        if (!validateCsrfToken($csrfToken, 'authenticate')) {
            renderLoginPage('Invalid CSRF token.');
            return;
        }

        $db = getDatabase();
        $stmt = $db->prepare('SELECT id, username, password_hash, role FROM users WHERE username = :username');
        $stmt->bindValue(':username', $username, SQLITE3_TEXT);
        $result = $stmt->execute();
        $user = $result->fetchArray(SQLITE3_ASSOC);

        if ($user && password_verify($password, $user['password_hash'])) {
            session_regenerate_id(true);
            $_SESSION['user_id'] = $user['id'];
            $_SESSION['username'] = $user['username'];
            $_SESSION['role'] = $user['role'];
            header('Location: /');
            return;
        }

        renderLoginPage('Invalid credentials.');
        return;
    }

    if (isAuthenticated()) {
        header('Location: /');
        return;
    }

    renderLoginPage();
}

function handleLogout(): void
{
    session_destroy();
    header('Location: /login');
}

function generateCsrfToken(string $intent): string
{
    if (!isset($_SESSION['csrf_tokens'])) {
        $_SESSION['csrf_tokens'] = [];
    }
    $token = bin2hex(random_bytes(32));
    $_SESSION['csrf_tokens'][$intent] = $token;
    return $token;
}

function validateCsrfToken(string $token, string $intent): bool
{
    return isset($_SESSION['csrf_tokens'][$intent]) &&
           hash_equals($_SESSION['csrf_tokens'][$intent], $token);
}

function renderLoginPage(string $error = ''): void
{
    $csrfToken = generateCsrfToken('authenticate');
    $lastUsername = htmlspecialchars($_POST['_username'] ?? '', ENT_QUOTES, 'UTF-8');
    include TEMPLATE_DIR . '/login.php';
}
