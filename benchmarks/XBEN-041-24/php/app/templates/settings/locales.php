<?php $pageTitle = 'Locales - Akeneo PIM'; $currentPage = 'locales'; ?>
<?php include __DIR__ . '/../layout/header.php'; ?>

<div class="page-header">
    <h1>Locales</h1>
</div>

<div class="card">
    <table>
        <thead>
            <tr>
                <th>Code</th>
                <th>Label</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($locales as $locale): ?>
            <tr>
                <td><strong><?= htmlspecialchars($locale['code']) ?></strong></td>
                <td><?= htmlspecialchars($locale['label']) ?></td>
                <td>
                    <?php if ($locale['activated']): ?>
                        <span class="badge badge-success">Activated</span>
                    <?php else: ?>
                        <span class="badge badge-danger">Deactivated</span>
                    <?php endif; ?>
                </td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</div>

<?php include __DIR__ . '/../layout/footer.php'; ?>