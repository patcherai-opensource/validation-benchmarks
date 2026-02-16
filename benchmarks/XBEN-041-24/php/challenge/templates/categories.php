<?php $pageTitle = 'Categories'; $requestUri = '/catalog/categories'; include TEMPLATE_DIR . '/layout_header.php'; ?>
        <h1>Categories</h1>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Code</th>
                    <th>Name</th>
                    <th>Parent</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($categories as $cat): ?>
                    <tr>
                        <td><?= htmlspecialchars($cat['code'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars($cat['name'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars($cat['parent_code'] ?? 'Root', ENT_QUOTES, 'UTF-8') ?></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
<?php include TEMPLATE_DIR . '/layout_footer.php'; ?>
