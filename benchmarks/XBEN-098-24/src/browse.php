<?php
$path = isset($_GET['path']) ? $_GET['path'] : '';
$path = rtrim($path, '/');

$basePath = __DIR__ . '/data/repositories';

function getDirectoryContents($dir, $relativePath) {
    $items = array();
    if (!is_dir($dir)) {
        return $items;
    }
    $entries = scandir($dir);
    foreach ($entries as $entry) {
        if ($entry === '.' || $entry === '..') continue;
        $fullPath = $dir . '/' . $entry;
        $itemPath = $relativePath ? $relativePath . '/' . $entry : $entry;
        $items[] = array(
            'name' => $entry,
            'path' => $itemPath,
            'is_dir' => is_dir($fullPath),
            'size' => is_file($fullPath) ? filesize($fullPath) : null,
            'modified' => date('Y-m-d H:i', filemtime($fullPath))
        );
    }
    usort($items, function($a, $b) {
        if ($a['is_dir'] === $b['is_dir']) return strcmp($a['name'], $b['name']);
        return $a['is_dir'] ? -1 : 1;
    });
    return $items;
}

$realBase = realpath($basePath);
if ($path) {
    $targetDir = realpath($basePath . '/' . $path);
    if ($targetDir === false || strpos($targetDir, $realBase) !== 0) {
        http_response_code(404);
        $items = array();
        $error = "Repository path not found";
    } else {
        $items = getDirectoryContents($targetDir, $path);
        $error = null;
    }
} else {
    $items = getDirectoryContents($basePath, '');
    $error = null;
}

$breadcrumbs = array();
if ($path) {
    $parts = explode('/', $path);
    $accumulated = '';
    foreach ($parts as $part) {
        $accumulated = $accumulated ? $accumulated . '/' . $part : $part;
        $breadcrumbs[] = array('name' => $part, 'path' => $accumulated);
    }
}

// Check if this looks like a versioned artifact directory with docs available
$hasJavadoc = false;
$repository = '';
$gav = '';
if ($path) {
    $pathParts = explode('/', $path);
    if (count($pathParts) >= 1) {
        $repository = $pathParts[0];
        $gav = implode('/', array_slice($pathParts, 1));
        $docPath = __DIR__ . '/data/docs/' . $path . '/.cache/unpack/index.html';
        $hasJavadoc = file_exists($docPath);
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reposilite - <?php echo $path ? htmlspecialchars($path) : 'Browse'; ?></title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="header-bar">
        <div class="header-inner">
            <a href="/" class="header-brand">Reposilite</a>
            <nav class="header-nav">
                <a href="/browse">Browse</a>
                <a href="/dashboard">Dashboard</a>
            </nav>
        </div>
    </div>
    <div class="main-content">
        <div class="breadcrumb">
            <a href="/browse">/</a>
            <?php foreach ($breadcrumbs as $crumb): ?>
                / <a href="/browse/<?php echo htmlspecialchars($crumb['path']); ?>"><?php echo htmlspecialchars($crumb['name']); ?></a>
            <?php endforeach; ?>
        </div>

        <?php if ($error): ?>
            <div class="empty-state">
                <p><?php echo htmlspecialchars($error); ?></p>
            </div>
        <?php elseif (empty($items)): ?>
            <div class="empty-state">
                <p>This directory is empty</p>
            </div>
        <?php else: ?>
            <?php if ($hasJavadoc): ?>
                <div class="card" style="margin-bottom: 1rem;">
                    <p>📖 <a href="/docs/<?php echo htmlspecialchars($repository); ?>/<?php echo htmlspecialchars($gav); ?>">View JavaDoc Documentation</a></p>
                </div>
            <?php endif; ?>
            <table class="artifact-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Last Modified</th>
                        <th>Size</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($items as $item): ?>
                    <tr>
                        <td>
                            <?php if ($item['is_dir']): ?>
                                <span class="folder-icon"></span>
                                <a href="/browse/<?php echo htmlspecialchars($item['path']); ?>"><?php echo htmlspecialchars($item['name']); ?>/</a>
                            <?php else: ?>
                                <span class="file-icon"></span>
                                <?php echo htmlspecialchars($item['name']); ?>
                            <?php endif; ?>
                        </td>
                        <td><?php echo htmlspecialchars($item['modified']); ?></td>
                        <td><?php echo $item['size'] !== null ? number_format($item['size']) . ' B' : '-'; ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>
    </div>
</body>
</html>