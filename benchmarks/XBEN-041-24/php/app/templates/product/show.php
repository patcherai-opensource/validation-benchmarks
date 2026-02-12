<?php $pageTitle = htmlspecialchars($product['label']) . ' - Akeneo PIM'; $currentPage = 'products'; ?>
<?php include __DIR__ . '/../layout/header.php'; ?>

<div class="page-header">
    <h1><?= htmlspecialchars($product['label']) ?></h1>
    <a href="/enrich/products" class="btn btn-secondary">Back to products</a>
</div>

<div style="display: grid; grid-template-columns: 2fr 1fr; gap: 24px;">
    <div>
        <div class="card">
            <h3 style="margin-bottom: 16px; font-weight: 400;">Product Information</h3>
            <table>
                <tr><th style="width: 160px;">Identifier</th><td><?= htmlspecialchars($product['identifier']) ?></td></tr>
                <tr><th>Family</th><td><?= htmlspecialchars($product['family']) ?></td></tr>
                <tr>
                    <th>Status</th>
                    <td>
                        <?php if ($product['status']): ?>
                            <span class="badge badge-success">Enabled</span>
                        <?php else: ?>
                            <span class="badge badge-warning">Disabled</span>
                        <?php endif; ?>
                    </td>
                </tr>
                <tr>
                    <th>Completeness</th>
                    <td>
                        <div class="progress-bar" style="width: 200px; display: inline-block; vertical-align: middle;">
                            <div class="fill" style="width: <?= (int)$product['completeness'] ?>%"></div>
                        </div>
                        <span style="font-size: 13px; margin-left: 8px;"><?= (int)$product['completeness'] ?>%</span>
                    </td>
                </tr>
                <tr><th>Created</th><td><?= htmlspecialchars($product['created']) ?></td></tr>
            </table>
        </div>

        <div class="card">
            <h3 style="margin-bottom: 16px; font-weight: 400;">Media</h3>

            <?php if (!empty($mediaFiles)): ?>
                <div class="media-grid">
                    <?php foreach ($mediaFiles as $media): ?>
                        <div class="media-item">
                            <img src="<?= htmlspecialchars($media['path']) ?>" alt="<?= htmlspecialchars($media['filename']) ?>" onerror="this.style.display='none'">
                            <div class="meta">
                                <?= htmlspecialchars($media['filename']) ?><br>
                                <span style="color: #a1b1c2;"><?= number_format($media['size'] / 1024, 1) ?> KB</span>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php else: ?>
                <p style="color: #a1b1c2; font-size: 13px;">No media files uploaded yet.</p>
            <?php endif; ?>

            <div class="upload-area" id="upload-area">
                <p style="color: #67768b; margin-bottom: 12px;">Drop a file here or click to upload</p>
                <form id="media-upload-form" enctype="multipart/form-data">
                    <input type="file" name="file" id="media-file-input" accept="image/*,.pdf" style="display:none;">
                    <button type="button" class="btn btn-primary" onclick="document.getElementById('media-file-input').click();">Select file</button>
                </form>
                <div id="upload-status" style="margin-top: 12px; font-size: 13px;"></div>
            </div>
        </div>
    </div>

    <div>
        <div class="card">
            <h3 style="margin-bottom: 16px; font-weight: 400;">Associations</h3>
            <p style="color: #a1b1c2; font-size: 13px;">No associations configured.</p>
        </div>
        <div class="card">
            <h3 style="margin-bottom: 16px; font-weight: 400;">History</h3>
            <div style="font-size: 13px; color: #67768b;">
                <p style="margin-bottom: 8px;"><strong>Julia Stark</strong> updated this product</p>
                <p style="font-size: 11px; color: #a1b1c2;">March 15, 2024 at 14:23</p>
            </div>
        </div>
    </div>
</div>

<script>
document.getElementById('media-file-input').addEventListener('change', function() {
    var form = document.getElementById('media-upload-form');
    var formData = new FormData(form);
    var status = document.getElementById('upload-status');

    status.textContent = 'Uploading...';
    status.style.color = '#67768b';

    fetch('/api/rest/v1/media-files', {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.code === 201) {
            status.textContent = 'File uploaded successfully.';
            status.style.color = '#1d8a2e';
            setTimeout(function() { window.location.reload(); }, 1000);
        } else {
            status.textContent = data.message || 'Upload failed.';
            status.style.color = '#c91c1c';
        }
    })
    .catch(function() {
        status.textContent = 'An error occurred during upload.';
        status.style.color = '#c91c1c';
    });
});
</script>

<?php include __DIR__ . '/../layout/footer.php'; ?>