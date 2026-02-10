<?php
session_start();

if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header("Location: admin.php");
    exit;
}

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);

if ($conn->connect_error) {
    http_response_code(500);
    die("Service temporarily unavailable");
}

$allowedTables = ['posts', 'comments', 'site_config', 'audit_log'];
$exportData = null;
$exportError = '';
$selectedTable = '';

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['data_source'])) {
    $dataSource = $_POST['data_source'];
    $selectedTable = $dataSource;
    
    if (empty($dataSource)) {
        $exportError = 'Please select a data source.';
    } else {
        $tableName = $dataSource;
        
        $countQuery = "SELECT COUNT(*) as total FROM `" . $tableName . "`";
        $countResult = $conn->query($countQuery);
        
        if ($countResult === false) {
            $exportError = 'Unable to export data from selected source.';
        } else {
            $countRow = $countResult->fetch_assoc();
            $totalRecords = $countRow['total'];
            
            $exportQuery = "SELECT * FROM `" . $tableName . "` LIMIT 100";
            $result = $conn->query($exportQuery);
            
            if ($result === false) {
                $exportError = 'Unable to export data from selected source.';
            } else {
                $exportData = [];
                while ($row = $result->fetch_assoc()) {
                    $exportData[] = $row;
                }
            }
        }
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Export - Admin</title>
    <link rel="stylesheet" href="styles.css">
    <style>
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f4f4f4; }
        .export-form { margin: 20px 0; }
        .error { color: red; }
    </style>
</head>
<body>
<div class="container">
    <h1>Data Export</h1>
    <p><a href="dashboard.php">&laquo; Back to Dashboard</a></p>

    <div class="export-form">
        <h2>Export Data</h2>
        <p>Select a data source to export records.</p>
        
        <form method="POST" action="data_export.php">
            <label for="data_source">Data Source:</label>
            <select name="data_source" id="data_source" required>
                <option value="">-- Select Data Source --</option>
                <?php foreach ($allowedTables as $table): ?>
                    <option value="<?php echo htmlspecialchars($table); ?>" <?php echo ($selectedTable === $table) ? 'selected' : ''; ?>>
                        <?php echo htmlspecialchars(ucfirst(str_replace('_', ' ', $table))); ?>
                    </option>
                <?php endforeach; ?>
            </select>
            <button type="submit">Export</button>
        </form>
    </div>

    <?php if ($exportError): ?>
        <p class="error"><?php echo htmlspecialchars($exportError); ?></p>
    <?php endif; ?>

    <?php if ($exportData !== null): ?>
        <h2>Export Results</h2>
        <?php if (count($exportData) > 0): ?>
            <p>Showing <?php echo count($exportData); ?> records from <?php echo htmlspecialchars($selectedTable); ?>.</p>
            <table>
                <thead>
                    <tr>
                        <?php foreach (array_keys($exportData[0]) as $col): ?>
                            <th><?php echo htmlspecialchars($col); ?></th>
                        <?php endforeach; ?>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($exportData as $row): ?>
                        <tr>
                            <?php foreach ($row as $value): ?>
                                <td><?php echo htmlspecialchars($value ?? ''); ?></td>
                            <?php endforeach; ?>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php else: ?>
            <p>No records found in the selected data source.</p>
        <?php endif; ?>
    <?php endif; ?>
</div>
</body>
</html>
