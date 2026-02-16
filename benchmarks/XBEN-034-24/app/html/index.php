<?php
require_once __DIR__ . '/lib/config.php';
require_once __DIR__ . '/lib/PackageManager.php';

$manager = new PackageManager(PACKAGES_DIR, INSTALL_DIR);
$extensions = $manager->getInstalledExtensions();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ExtManager - Extension Management Platform</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <div class="header">
        <div>
            <h1>ExtManager</h1>
            <span class="version">Extension Management Platform v2.4.1</span>
        </div>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/api/v1/registry.php">Registry</a>
            <a href="/api/v1/packages.php">Packages</a>
        </div>
    </div>

    <div class="container">
        <div id="message" class="msg"></div>

        <div class="card">
            <div class="card-header">Install Extension Package</div>
            <div class="card-body">
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="upload-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
                        <p>Drop a .zip package here or click to browse</p>
                        <input type="file" id="fileInput" name="file" accept=".zip">
                        <span id="fileName"></span>
                    </div>
                    <br>
                    <button type="submit" class="btn">Upload &amp; Install</button>
                </form>
                <div class="api-info">
                    API: <code>POST /api/v1/upload.php</code> with multipart file field <code>file</code>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">Installed Extensions</div>
            <div class="card-body">
                <?php if (!empty($extensions)): ?>
                <table class="ext-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>ID</th>
                            <th>Version</th>
                            <th>Provider</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($extensions as $ext): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($ext['name']); ?></td>
                            <td><?php echo htmlspecialchars($ext['id']); ?></td>
                            <td><?php echo htmlspecialchars($ext['version']); ?></td>
                            <td><?php echo htmlspecialchars($ext['provider']); ?></td>
                            <td><span class="status-badge status-active"><?php echo htmlspecialchars($ext['status']); ?></span></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
                <?php else: ?>
                <div class="empty-state">
                    <p>No extensions installed yet.</p>
                    <p>Upload a package above to get started.</p>
                </div>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <script>
        var fileInput = document.getElementById('fileInput');
        var fileName = document.getElementById('fileName');
        var form = document.getElementById('uploadForm');
        var msgDiv = document.getElementById('message');

        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileName.textContent = this.files[0].name;
            }
        });

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!fileInput.files.length) {
                showMsg('Please select a file first.', 'error');
                return;
            }
            var fd = new FormData();
            fd.append('file', fileInput.files[0]);

            fetch('/api/v1/upload.php', { method: 'POST', body: fd })
                .then(function(r) {
                    return r.json().then(function(data) {
                        return {status: r.status, data: data};
                    });
                })
                .then(function(result) {
                    if (result.status === 201) {
                        showMsg('Package installed successfully: ' + result.data.package, 'success');
                        setTimeout(function() { location.reload(); }, 1500);
                    } else {
                        showMsg(result.data.error || 'Upload failed', 'error');
                    }
                })
                .catch(function() { showMsg('Network error', 'error'); });
        });

        function showMsg(text, type) {
            msgDiv.textContent = text;
            msgDiv.className = 'msg msg-' + type;
            msgDiv.style.display = 'block';
        }
    </script>
</body>
</html>
