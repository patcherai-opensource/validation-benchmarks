<?php
$servername = getenv('MYSQL_HOST');
$db_username = getenv('MYSQL_USER');
$db_password = getenv('MYSQL_PASSWORD');
$dbname = getenv('MYSQL_DATABASE');

$conn = new mysqli($servername, $db_username, $db_password, $dbname);

if ($conn->connect_error) {
    die("Service temporarily unavailable");
}

$results = [];
$search_query = "";

if (isset($_REQUEST["q"]) && !empty($_REQUEST["q"])) {
    $search_query = $_REQUEST["q"];
    $stmt = $conn->prepare("SELECT id, name, email FROM customers WHERE name LIKE ? OR email LIKE ?");
    $search_param = "%" . $search_query . "%";
    $stmt->bind_param("ss", $search_param, $search_param);
    $stmt->execute();
    $result = $stmt->get_result();
    
    while ($row = $result->fetch_assoc()) {
        $results[] = $row;
    }
    $stmt->close();
}

$conn->close();
?>
<!DOCTYPE html>
<html>
<head>
    <title>Customer Search - Customer Management Framework</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
        input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .results { margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
        .no-results { color: #666; font-style: italic; }
        .back { margin-top: 20px; }
        .back a { color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Public Customer Search</h1>
        <p>Search for customers in our directory.</p>
        
        <form method="GET" action="search.php">
            <div class="form-group">
                <label for="q">Search:</label>
                <input type="text" name="q" id="q" placeholder="Enter name or email" value="<?php echo htmlspecialchars($search_query); ?>">
            </div>
            <button type="submit">Search</button>
        </form>
        
        <?php if ($search_query !== ""): ?>
        <div class="results">
            <h3>Search Results</h3>
            <?php if (count($results) > 0): ?>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($results as $row): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($row['id']); ?></td>
                        <td><?php echo htmlspecialchars($row['name']); ?></td>
                        <td><?php echo htmlspecialchars($row['email']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <?php else: ?>
            <p class="no-results">No customers found matching your search.</p>
            <?php endif; ?>
        </div>
        <?php endif; ?>
        
        <div class="back">
            <a href="/index.php">&larr; Back to Home</a>
        </div>
    </div>
</body>
</html>
