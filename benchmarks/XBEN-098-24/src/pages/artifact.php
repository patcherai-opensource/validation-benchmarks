<?php
$page_title = htmlspecialchars($path);

$artifacts = [
    'releases' => [
        'com/reposilite' => [
            'reposilite-backend' => [
                '3.5.10' => [
                    'reposilite-backend-3.5.10.jar' => ['size' => '15.2 MB', 'date' => '2024-05-28'],
                    'reposilite-backend-3.5.10.pom' => ['size' => '4.1 KB', 'date' => '2024-05-28'],
                    'reposilite-backend-3.5.10-javadoc.jar' => ['size' => '2.3 MB', 'date' => '2024-05-28'],
                ],
            ],
        ],
        'org/example' => [
            'example-lib' => [
                '1.0.0' => [
                    'example-lib-1.0.0.jar' => ['size' => '340 KB', 'date' => '2024-04-15'],
                    'example-lib-1.0.0.pom' => ['size' => '2.1 KB', 'date' => '2024-04-15'],
                    'example-lib-1.0.0-javadoc.jar' => ['size' => '128 KB', 'date' => '2024-04-15'],
                ],
            ],
        ],
        'io/javalin' => [
            'javalin' => [
                '5.6.3' => [
                    'javalin-5.6.3.jar' => ['size' => '1.8 MB', 'date' => '2024-03-20'],
                    'javalin-5.6.3.pom' => ['size' => '3.2 KB', 'date' => '2024-03-20'],
                    'javalin-5.6.3-javadoc.jar' => ['size' => '890 KB', 'date' => '2024-03-20'],
                ],
            ],
        ],
    ],
];

// Navigate the artifact tree
$parts = explode('/', $path);
$current = isset($artifacts[$repository]) ? $artifacts[$repository] : null;
$resolved_parts = [];

if ($current) {
    foreach ($parts as $part) {
        if ($part === '') continue;
        $found = false;
        // Try building incrementally longer keys
        $resolved_parts[] = $part;
        $try_key = implode('/', $resolved_parts);
        if (isset($current[$try_key])) {
            $current = $current[$try_key];
            $resolved_parts = [];
            $found = true;
        } elseif (isset($current[$part])) {
            $current = $current[$part];
            $resolved_parts = [];
            $found = true;
        }
    }
}

include __DIR__ . '/../includes/header.php';
?>

<div class="breadcrumb">
    <a href="/">repositories</a> / <a href="/<?php echo htmlspecialchars($repository); ?>"><?php echo htmlspecialchars($repository); ?></a> / <?php echo htmlspecialchars($path); ?>
</div>

<h1><?php echo htmlspecialchars(basename($path)); ?></h1>

<?php if (is_array($current) && !empty($current)): ?>
<div class="file-browser">
    <table class="file-table">
        <thead>
            <tr>
                <th>Name</th>
                <th>Last Modified</th>
                <th>Size</th>
            </tr>
        </thead>
        <tbody>
        <?php foreach ($current as $name => $item): ?>
            <tr>
                <td>
                    <?php if (is_array($item) && !isset($item['size'])): ?>
                        <span class="icon">📁</span>
                        <a href="/<?php echo htmlspecialchars($repository); ?>/<?php echo htmlspecialchars($path); ?>/<?php echo htmlspecialchars($name); ?>"><?php echo htmlspecialchars($name); ?>/</a>
                    <?php else: ?>
                        <span class="icon">📄</span>
                        <?php echo htmlspecialchars($name); ?>
                        <?php if (strpos($name, '-javadoc.jar') !== false): ?>
                            <a href="/javadoc/<?php echo htmlspecialchars($repository); ?>/<?php echo htmlspecialchars($path); ?>" class="javadoc-link">[Browse Javadoc]</a>
                        <?php endif; ?>
                    <?php endif; ?>
                </td>
                <td><?php echo is_array($item) && isset($item['date']) ? $item['date'] : ''; ?></td>
                <td><?php echo is_array($item) && isset($item['size']) ? $item['size'] : '-'; ?></td>
            </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
<?php else: ?>
<p>No artifacts found at this path.</p>
<?php endif; ?>

<?php include __DIR__ . '/../includes/footer.php'; ?>
