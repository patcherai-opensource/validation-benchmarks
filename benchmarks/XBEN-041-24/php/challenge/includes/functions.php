<?php
/**
 * myKnowledgeBase Core Functions
 *
 * @package   myKnowledgeBase
 */

/**
 * Generate a CSRF token and store it in the session
 */
function mkb_generate_token(string $formId): string
{
    $token = bin2hex(random_bytes(32));
    $_SESSION['csrf_tokens'][$formId] = $token;
    return $token;
}

/**
 * Verify a CSRF token
 */
function mkb_verify_token(string $formId, ?string $token): bool
{
    if ($token === null || !isset($_SESSION['csrf_tokens'][$formId])) {
        return false;
    }
    $valid = hash_equals($_SESSION['csrf_tokens'][$formId], $token);
    if ($valid) {
        unset($_SESSION['csrf_tokens'][$formId]);
    }
    return $valid;
}

/**
 * Check if admin is logged in
 */
function mkb_is_admin_logged_in(): bool
{
    return isset($_SESSION['admin_authenticated']) && $_SESSION['admin_authenticated'] === true;
}

/**
 * Get current admin username
 */
function mkb_get_admin_user(): ?string
{
    return $_SESSION['admin_user'] ?? null;
}

/**
 * Sanitize input
 */
function mkb_filter_input(string $value, int $filter = FILTER_SANITIZE_SPECIAL_CHARS): string
{
    return filter_var($value, $filter) ?: '';
}

/**
 * Render a topic tree
 */
function mkb_render_topic_tree(array $topics, int $parentId = 0, int $depth = 0): string
{
    $html = '';
    foreach ($topics as $id => $topic) {
        if ($topic['parent_id'] == $parentId) {
            $indent = str_repeat('&nbsp;&nbsp;&nbsp;&nbsp;', $depth);
            $activeLabel = $topic['active'] ? '' : ' <span class="badge-inactive">inactive</span>';
            $image = '';
            if (!empty($topic['image']) && file_exists(MKB_IMAGES_DIR . $topic['image'])) {
                $image = '<img src="/images/' . htmlspecialchars($topic['image']) . '" class="topic-thumb" alt="">';
            }
            $html .= '<div class="topic-item" data-id="' . $id . '">';
            $html .= $indent . $image . '<a href="/?action=overview&topic=' . $id . '">' . htmlspecialchars($topic['name']) . '</a>';
            $html .= ' <span class="topic-lang">(' . htmlspecialchars($topic['lang']) . ')</span>';
            $html .= $activeLabel;
            $html .= '</div>';
            $html .= mkb_render_topic_tree($topics, $id, $depth + 1);
        }
    }
    return $html;
}
