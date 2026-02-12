<?php
    include 'config.php';
    include 'user-profile.php';
    include 'misc.php';

    $conn = getDbConnection();
    $user = requireAuth($conn);

    $channel = isset($_GET['channel']) ? trim($_GET['channel']) : 'general';
    $channel = preg_replace('/[^a-zA-Z0-9_-]/', '', $channel);
    if (empty($channel)) $channel = 'general';

    // Handle new message posting
    if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['content'])) {
        $content = trim($_POST['content']);
        if (!empty($content) && strlen($content) <= 4000) {
            $stmt = $conn->prepare("INSERT INTO chat_messages (user_id, channel, content) VALUES (?, ?, ?)");
            $stmt->bind_param("iss", $user['id'], $channel, $content);
            $stmt->execute();
            $stmt->close();
        }
        header("Location: /?channel=" . urlencode($channel));
        exit();
    }

    // Fetch messages for this channel
    $stmt = $conn->prepare("SELECT m.id, m.content, m.created_at, u.username, u.role, u.profile_image_url FROM chat_messages m INNER JOIN users u ON m.user_id = u.id WHERE m.channel = ? ORDER BY m.created_at ASC LIMIT 100");
    $stmt->bind_param("s", $channel);
    $stmt->execute();
    $messages = $stmt->get_result();
    $stmt->close();

    // Simple markdown renderer
    function renderMarkdown($text) {
        // Convert markdown to HTML - supports common markdown syntax
        $html = $text;

        // Images: ![alt](url) -> <img src="url" alt="alt">
        $html = preg_replace('/!\[([^\]]*)\]\(([^)]+)\)/', '<img src="$2" alt="$1" class="chat-image">', $html);

        // Links: [text](url) -> <a href="url">text</a>
        $html = preg_replace('/\[([^\]]+)\]\(([^)]+)\)/', '<a href="$2" target="_blank" rel="noopener">$1</a>', $html);

        // Bold: **text** -> <strong>text</strong>
        $html = preg_replace('/\*\*(.+?)\*\*/', '<strong>$1</strong>', $html);

        // Italic: *text* -> <em>text</em>
        $html = preg_replace('/\*(.+?)\*/', '<em>$1</em>', $html);

        // Inline code: `code` -> <code>code</code>
        $html = preg_replace('/`([^`]+)`/', '<code>$1</code>', $html);

        // Code blocks: ```code``` -> <pre><code>code</code></pre>
        $html = preg_replace('/```([\s\S]+?)```/', '<pre><code>$1</code></pre>', $html);

        // Headers
        $html = preg_replace('/^### (.+)$/m', '<h3>$1</h3>', $html);
        $html = preg_replace('/^## (.+)$/m', '<h2>$1</h2>', $html);
        $html = preg_replace('/^# (.+)$/m', '<h1>$1</h1>', $html);

        // Line breaks
        $html = nl2br($html);

        return $html;
    }

    $conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $app_name; ?></title>
    <link rel="stylesheet" href="/static/styles.css">
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
</head>
<body>
    <div class="app-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <img src="/static/logo.svg" alt="Open WebUI" class="sidebar-logo">
                <span class="sidebar-title"><?php echo $app_name; ?></span>
            </div>
            <div class="sidebar-nav">
                <a href="/?channel=general" class="nav-item <?php echo $channel === 'general' ? 'active' : ''; ?>">
                    <span class="nav-icon">#</span> general
                </a>
                <a href="/?channel=random" class="nav-item <?php echo $channel === 'random' ? 'active' : ''; ?>">
                    <span class="nav-icon">#</span> random
                </a>
                <a href="/?channel=help" class="nav-item <?php echo $channel === 'help' ? 'active' : ''; ?>">
                    <span class="nav-icon">#</span> help
                </a>
            </div>
            <div class="sidebar-footer">
                <div class="user-info">
                    <span class="user-avatar"><?php echo strtoupper(substr($user['username'], 0, 1)); ?></span>
                    <span class="user-name"><?php echo htmlspecialchars($user['username']); ?></span>
                    <?php if ($user['role'] === 'admin'): ?>
                        <span class="badge badge-admin">admin</span>
                    <?php endif; ?>
                </div>
                <?php if ($user['role'] === 'admin'): ?>
                    <a href="/admin.php" class="nav-item nav-admin">Settings</a>
                <?php endif; ?>
                <a href="/logout.php" class="nav-item nav-logout">Sign Out</a>
            </div>
        </nav>

        <main class="chat-main">
            <div class="chat-header">
                <h2># <?php echo htmlspecialchars($channel); ?></h2>
            </div>

            <div class="chat-messages" id="chat-messages">
                <?php if ($messages->num_rows === 0): ?>
                    <div class="empty-state">
                        <p>No messages yet. Be the first to post!</p>
                    </div>
                <?php else: ?>
                    <?php while ($msg = $messages->fetch_assoc()): ?>
                        <div class="message">
                            <div class="message-header">
                                <span class="message-avatar"><?php echo strtoupper(substr($msg['username'], 0, 1)); ?></span>
                                <span class="message-author <?php echo $msg['role'] === 'admin' ? 'author-admin' : ''; ?>">
                                    <?php echo htmlspecialchars($msg['username']); ?>
                                    <?php if ($msg['role'] === 'admin'): ?>
                                        <span class="badge badge-admin">admin</span>
                                    <?php endif; ?>
                                </span>
                                <span class="message-time"><?php echo date('M j, g:i A', strtotime($msg['created_at'])); ?></span>
                            </div>
                            <div class="message-body">
                                <?php echo renderMarkdown($msg['content']); ?>
                            </div>
                        </div>
                    <?php endwhile; ?>
                <?php endif; ?>
            </div>

            <div class="chat-input-area">
                <form method="post" action="/?channel=<?php echo urlencode($channel); ?>" class="message-form">
                    <div class="input-wrapper">
                        <textarea name="content" placeholder="Send a message to #<?php echo htmlspecialchars($channel); ?>... (Markdown supported)" rows="2" required maxlength="4000"></textarea>
                        <button type="submit" class="btn btn-send" title="Send">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13"/><path d="M22 2L15 22L11 13L2 9L22 2Z"/></svg>
                        </button>
                    </div>
                    <p class="input-hint">Markdown formatting is supported. Use **bold**, *italic*, `code`, images, and more.</p>
                </form>
            </div>
        </main>
    </div>

    <script>
        // Auto-scroll to bottom
        var chatMessages = document.getElementById('chat-messages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    </script>
</body>
</html>