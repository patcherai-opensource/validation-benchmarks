<?php
$page_title = htmlspecialchars($repository);

$repositories = [
    'releases' => [
        'com/reposilite' => ['name' => 'com/reposilite', 'type' => 'directory'],
        'org/example' => ['name' => 'org/example', 'type' => 'directory'],
        'io/javalin' => ['name' => 'io/javalin', 'type' => 'directory'],
    ],
    'snapshots' => [
        'com/reposilite' => ['name' => 'com/reposilite', 'type' => 'directory'],
        'org/example' => ['name' => 'org/example', 'type' => 'directory'],
    ],
];

if (!isset($repositories[$repository])) {
    http_response_code(404);
    include __DIR__ . '/404.php';
    exit;
}

include __DIR__ . '/../includes/header.php';
?>

<div class="breadcrumb">
    <a href="/">repositories</a> / <strong><?php echo htmlspecialchars($repository); ?></strong>
</div>

<h1><?php echo htmlspecialchars($repository); ?></h1>

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
        <?php foreach ($repositories[$repository] as $key => $item): ?>
            <tr>
                <td>
                    <span class="icon">📁</span>
                    <a href="/<?php echo htmlspecialchars($repository); ?>/<?php echo htmlspecialchars($key); ?>"><?php echo htmlspecialchars($item['name']); ?>/</a>
                </td>
                <td>2024-06-01 14:30</td>
                <td>-</td>
            </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>

<?php include __DIR__ . '/../includes/footer.php'; ?>
