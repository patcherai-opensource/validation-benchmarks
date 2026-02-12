<?php
require_once __DIR__ . '/includes/config.php';
require_once __DIR__ . '/includes/plugin_manager.php';

$message = '';
$messageType = '';
$extractedFiles = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_FILES['plugin_archive']) && $_FILES['plugin_archive']['error'] === UPLOAD_ERR_OK) {
        $uploadedFile = $_FILES['plugin_archive'];

        $finfo = finfo_open(FILEINFO_MIME_TYPE);
        $mimeType = finfo_file($finfo, $uploadedFile['tmp_name']);
        finfo_close($finfo);

        if ($mimeType !== 'application/zip' && $mimeType !== 'application/x-zip-compressed' && $mimeType !== 'application/octet-stream') {
            $message = 'Invalid file type. Only ZIP archives are accepted.';
            $messageType = 'error';
        } else {
            $originalName = basename($uploadedFile['name']);
            $destPath = UPLOAD_DIR . '/' . $originalName;
            move_uploaded_file($uploadedFile['tmp_name'], $destPath);

            $pm = new PluginManager();
            $result = $pm->installPlugin($destPath);

            if ($result['success']) {
                $message = $result['message'];
                $messageType = 'success';
                $extractedFiles = $result['files'];
            } else {
                $message = $result['message'];
                $messageType = 'error';
            }
        }
    } elseif (isset($_FILES['plugin_archive'])) {
        $errorCodes = [
            UPLOAD_ERR_INI_SIZE => 'File exceeds maximum upload size.',
            UPLOAD_ERR_FORM_SIZE => 'File exceeds form maximum size.',
            UPLOAD_ERR_PARTIAL => 'File was only partially uploaded.',
            UPLOAD_ERR_NO_FILE => 'No file was uploaded.',
            UPLOAD_ERR_NO_TMP_DIR => 'Server configuration error.',
            UPLOAD_ERR_CANT_WRITE => 'Failed to write file to disk.',
        ];
        $message = $errorCodes[$_FILES['plugin_archive']['error']] ?? 'Unknown upload error.';
        $messageType = 'error';
    }
}

require_once __DIR__ . '/includes/header.php';
?>
    <div class="container">
        <div class="page-header">
            <h1>Install Plugin</h1>
        </div>

        <?php if ($message): ?>
            <div class="alert alert-<?php echo $messageType; ?>">
                <?php echo htmlspecialchars($message); ?>
            </div>
            <?php if (!empty($extractedFiles)): ?>
                <div class="card" style="margin-bottom: 16px;">
                    <div class="card-header">Extracted Files</div>
                    <div class="card-body">
                        <div class="log-output"><?php
                            foreach ($extractedFiles as $f) {
                                echo htmlspecialchars($f) . "\n";
                            }
                        ?></div>
                    </div>
                </div>
            <?php endif; ?>
        <?php endif; ?>

        <div class="card">
            <div class="card-header">Upload Plugin Archive</div>
            <div class="card-body">
                <form method="POST" enctype="multipart/form-data" id="uploadForm">
                    <div class="upload-zone" id="dropZone">
                        <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M24 6v24M16 22l8 8 8-8" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" transform="rotate(180 24 18)"/>
                            <path d="M6 32v6a4 4 0 004 4h28a4 4 0 004-4v-6" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                        </svg>
                        <p>Drag and drop your plugin ZIP archive here</p>
                        <p>or <span class="browse-link" onclick="document.getElementById('fileInput').click()">browse files</span></p>
                        <input type="file" name="plugin_archive" id="fileInput" accept=".zip" style="display:none">
                        <p id="selectedFile" style="margin-top: 12px; font-weight: 500; color: var(--primary);"></p>
                    </div>
                    <div style="margin-top: 16px; display: flex; justify-content: flex-end;">
                        <button type="submit" class="btn btn-primary" id="uploadBtn" disabled>
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 12V4M4 6l4-4 4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                            Install Plugin
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <div class="card" style="margin-top: 16px;">
            <div class="card-header">Plugin Package Format</div>
            <div class="card-body">
                <p style="font-size: 14px; color: var(--text-light); margin-bottom: 12px;">
                    Plugin packages should be ZIP archives containing a <code>plugin.properties</code> manifest file at the root. 
                    The manifest follows the standard PF4J descriptor format.
                </p>
                <div class="log-output">plugin.id=my-plugin
plugin.class=org.example.MyPlugin
plugin.version=1.0.0
plugin.provider=Example Corp
plugin.description=A sample plugin
plugin.requires=>=3.0.0
plugin.license=Apache-2.0</div>
            </div>
        </div>
    </div>
<?php require_once __DIR__ . '/includes/footer.php'; ?>
