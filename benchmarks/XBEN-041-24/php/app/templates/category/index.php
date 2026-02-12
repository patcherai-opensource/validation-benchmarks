<?php $pageTitle = 'Categories - Akeneo PIM'; $currentPage = 'categories'; ?>
<?php include __DIR__ . '/../layout/header.php'; ?>

<div class="page-header">
    <h1>Category Trees</h1>
</div>

<div class="card">
    <table>
        <thead>
            <tr>
                <th>Code</th>
                <th>Label</th>
                <th>Parent</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($categories as $category): ?>
            <tr>
                <td><strong><?= htmlspecialchars($category['code']) ?></strong></td>
                <td><?= htmlspecialchars($category['label']) ?></td>
                <td><?= htmlspecialchars($category['parent'] ?? '—') ?></td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</div>

<?php include __DIR__ . '/../layout/footer.php'; ?>