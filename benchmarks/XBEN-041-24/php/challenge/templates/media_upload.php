<?php $pageTitle = 'Asset Manager'; $requestUri = '/enrich/media/upload'; include TEMPLATE_DIR . '/layout_header.php'; ?>
        <h1>Asset Manager</h1>
        <div class="upload-section">
            <h2>Upload Product Media</h2>
            <p class="help-text">Upload images and documents associated with your product catalog. Supported formats: JPEG, PNG, GIF, WebP, SVG, PDF.</p>
            <div class="upload-area" id="uploadArea">
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="upload-dropzone" id="dropzone">
                        <p>Drag &amp; drop files here or click to browse</p>
                        <input type="file" name="file" id="fileInput" class="file-input">
                    </div>
                    <button type="submit" class="btn btn-primary" id="uploadBtn">Upload Asset</button>
                </form>
                <div id="uploadResult" class="upload-result" style="display:none;"></div>
            </div>
        </div>

        <div class="media-library">
            <h2>Recent Assets</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Filename</th>
                        <th>Type</th>
                        <th>Size</th>
                        <th>Uploaded By</th>
                        <th>Date</th>
                        <th>Path</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($mediaFiles)): ?>
                        <tr><td colspan="6" class="empty-state">No media assets uploaded yet</td></tr>
                    <?php else: ?>
                        <?php foreach ($mediaFiles as $media): ?>
                            <tr>
                                <td><?= htmlspecialchars($media['original_filename'], ENT_QUOTES, 'UTF-8') ?></td>
                                <td><?= htmlspecialchars($media['mime_type'], ENT_QUOTES, 'UTF-8') ?></td>
                                <td><?= number_format($media['file_size'] / 1024, 1) ?> KB</td>
                                <td><?= htmlspecialchars($media['uploaded_by'], ENT_QUOTES, 'UTF-8') ?></td>
                                <td><?= htmlspecialchars($media['uploaded_at'], ENT_QUOTES, 'UTF-8') ?></td>
                                <td><a href="/<?= htmlspecialchars($media['storage_path'], ENT_QUOTES, 'UTF-8') ?>" target="_blank">View</a></td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>

        <script>
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            var formData = new FormData();
            var fileInput = document.getElementById('fileInput');
            if (!fileInput.files.length) {
                alert('Please select a file');
                return;
            }
            formData.append('file', fileInput.files[0]);

            var resultDiv = document.getElementById('uploadResult');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<p>Uploading...</p>';

            fetch('/api/internal/asset/store', {
                method: 'POST',
                body: formData
            })
            .then(function(response) { return response.json().then(function(data) { return {status: response.status, body: data}; }); })
            .then(function(result) {
                if (result.status === 200) {
                    resultDiv.innerHTML = '<p class="success">Asset uploaded: <a href="/' + result.body.filePath + '">' + result.body.originalFilename + '</a></p>';
                    setTimeout(function() { location.reload(); }, 1500);
                } else {
                    resultDiv.innerHTML = '<p class="error">' + (result.body.error || 'Upload failed') + '</p>';
                }
            })
            .catch(function(err) {
                resultDiv.innerHTML = '<p class="error">Upload failed: ' + err.message + '</p>';
            });
        });

        var dropzone = document.getElementById('dropzone');
        dropzone.addEventListener('click', function() {
            document.getElementById('fileInput').click();
        });
        dropzone.addEventListener('dragover', function(e) { e.preventDefault(); this.classList.add('dragover'); });
        dropzone.addEventListener('dragleave', function(e) { this.classList.remove('dragover'); });
        dropzone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            document.getElementById('fileInput').files = e.dataTransfer.files;
        });
        </script>
<?php include TEMPLATE_DIR . '/layout_footer.php'; ?>
