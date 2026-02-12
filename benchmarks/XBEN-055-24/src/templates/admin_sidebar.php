<div class="admin-sidebar">
    <a href="/admin" <?php echo (strpos($_SERVER['REQUEST_URI'], '/admin/') === false && $_SERVER['REQUEST_URI'] === '/admin') ? 'class="active"' : ''; ?>>Dashboard</a>
    <a href="/admin/pages" <?php echo strpos($_SERVER['REQUEST_URI'], '/admin/pages') !== false ? 'class="active"' : ''; ?>>Pages</a>
    <?php if ($member['MemberGroup'] === 'administrators'): ?>
    <a href="/admin/notes" <?php echo strpos($_SERVER['REQUEST_URI'], '/admin/notes') !== false ? 'class="active"' : ''; ?>>My Notes</a>
    <a href="/admin/settings" <?php echo strpos($_SERVER['REQUEST_URI'], '/admin/settings') !== false ? 'class="active"' : ''; ?>>Settings</a>
    <?php endif; ?>
</div>