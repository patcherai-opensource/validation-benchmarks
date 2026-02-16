<?php
$repository = isset($_GET['repository']) ? $_GET['repository'] : null;
$gav = isset($_GET['gav']) ? $_GET['gav'] : null;

if (!$repository || !$gav) {
    http_response_code(400);
    header('Content-Type: application/json');
    echo json_encode(array('status' => 400, 'message' => 'Missing repository or GAV parameter'));
    exit;
}

$allowedRepos = array('releases', 'snapshots', 'public');
if (!in_array($repository, $allowedRepos)) {
    http_response_code(404);
    header('Content-Type: application/json');
    echo json_encode(array('status' => 404, 'message' => 'Repository not found'));
    exit;
}

$docsBase = __DIR__ . '/data/docs';
$cacheIndex = $docsBase . '/' . $repository . '/' . $gav . '/.cache/unpack/index.html';

$realDocsBase = realpath($docsBase);
$realIndex = realpath(dirname($cacheIndex));

if ($realIndex === false || strpos($realIndex, $realDocsBase) !== 0) {
    http_response_code(404);
    header('Content-Type: application/json');
    echo json_encode(array('status' => 404, 'message' => 'Documentation not found for this artifact'));
    exit;
}

if (!file_exists($cacheIndex)) {
    http_response_code(404);
    header('Content-Type: application/json');
    echo json_encode(array('status' => 404, 'message' => 'Documentation not found for this artifact'));
    exit;
}

$assetsBase = '/docs/' . rawurlencode($repository) . '/' . $gav . '/assets';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Reposilite - JavaDoc</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body style="margin:0; overflow:hidden;">
    <div class="header-bar">
        <div class="header-inner">
            <a href="/" class="header-brand">Reposilite</a>
            <nav class="header-nav">
                <a href="/browse">Browse</a>
                <a href="/browse/<?php echo htmlspecialchars($repository . '/' . $gav); ?>">Artifact</a>
                <a href="<?php echo htmlspecialchars($assetsBase . '/index.html'); ?>">Raw docs</a>
            </nav>
        </div>
    </div>
    <iframe class="doc-frame" src="<?php echo htmlspecialchars($assetsBase . '/index.html'); ?>" sandbox="allow-scripts"></iframe>
</body>
</html>