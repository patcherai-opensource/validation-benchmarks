<?php $pageTitle = 'Attributes'; $requestUri = '/catalog/attributes'; include TEMPLATE_DIR . '/layout_header.php'; ?>
        <h1>Attributes</h1>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Code</th>
                    <th>Label</th>
                    <th>Type</th>
                    <th>Group</th>
                    <th>Required</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($attributes as $attr): ?>
                    <tr>
                        <td><?= htmlspecialchars($attr['code'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars($attr['label'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars($attr['type'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars($attr['attribute_group'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= $attr['is_required'] ? 'Yes' : 'No' ?></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
<?php include TEMPLATE_DIR . '/layout_footer.php'; ?>
