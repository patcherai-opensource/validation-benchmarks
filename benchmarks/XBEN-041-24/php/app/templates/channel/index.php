<?php $pageTitle = 'Channels - Akeneo PIM'; $currentPage = 'channels'; ?>
<?php include __DIR__ . '/../layout/header.php'; ?>

<div class="page-header">
    <h1>Channels</h1>
</div>

<div class="card">
    <table>
        <thead>
            <tr>
                <th>Code</th>
                <th>Label</th>
                <th>Currencies</th>
                <th>Locales</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($channels as $channel): ?>
            <tr>
                <td><strong><?= htmlspecialchars($channel['code']) ?></strong></td>
                <td><?= htmlspecialchars($channel['label']) ?></td>
                <td><?= htmlspecialchars(implode(', ', $channel['currencies'])) ?></td>
                <td><?= htmlspecialchars(implode(', ', $channel['locales'])) ?></td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</div>

<?php include __DIR__ . '/../layout/footer.php'; ?>