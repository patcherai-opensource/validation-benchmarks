<?php $pageTitle = 'Products - Akeneo PIM'; $currentPage = 'products'; ?>
<?php include __DIR__ . '/../layout/header.php'; ?>

<div class="page-header">
    <h1>Products</h1>
</div>

<div class="card">
    <table>
        <thead>
            <tr>
                <th>Identifier</th>
                <th>Label</th>
                <th>Family</th>
                <th>Status</th>
                <th>Completeness</th>
                <th>Created</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($products as $id => $product): ?>
            <tr>
                <td><strong><?= htmlspecialchars($product['identifier']) ?></strong></td>
                <td><?= htmlspecialchars($product['label']) ?></td>
                <td><?= htmlspecialchars($product['family']) ?></td>
                <td>
                    <?php if ($product['status']): ?>
                        <span class="badge badge-success">Enabled</span>
                    <?php else: ?>
                        <span class="badge badge-warning">Disabled</span>
                    <?php endif; ?>
                </td>
                <td>
                    <div class="progress-bar">
                        <div class="fill" style="width: <?= (int)$product['completeness'] ?>%"></div>
                    </div>
                    <span style="font-size: 11px; color: #67768b;"><?= (int)$product['completeness'] ?>%</span>
                </td>
                <td style="font-size: 13px; color: #67768b;"><?= htmlspecialchars($product['created']) ?></td>
                <td><a href="/enrich/products/<?= $id ?>" class="btn btn-secondary" style="font-size: 12px; padding: 4px 12px;">View</a></td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</div>

<?php include __DIR__ . '/../layout/footer.php'; ?>