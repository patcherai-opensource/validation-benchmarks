<?php
    $conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'ezcmsDB');
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eZCMS - Content Portal</title>
    <link rel="stylesheet" href="styles.css">
    <style>
        .header { 
            background: #2c3e50; 
            color: white; 
            padding: 20px; 
            margin: -20px -20px 20px -20px;
            border-radius: 8px 8px 0 0;
        }
        .header h1 { margin: 0; }
        .header .tagline { font-size: 0.9em; color: #bdc3c7; }
        .nav-links { margin-top: 10px; }
        .nav-links a { color: #3498db; margin-right: 15px; text-decoration: none; }
        .nav-links a:hover { text-decoration: underline; }
        .content-item { 
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-bottom: 20px;
        }
        .section-badge {
            display: inline-block;
            background: #e8f4f8;
            color: #2980b9;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>eZCMS</h1>
        <p class="tagline">Enterprise Content Management System</p>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/admin.php">Administration</a>
        </div>
    </div>

    <h2>Published Content</h2>

    <form action="" method="GET">
        <label for="section">Filter by section:</label>
        <select name="section" id="section" onchange="this.form.submit()">
            <option value="">All Sections</option>        
            <?php
            $section_result = $conn->query("SELECT DISTINCT section FROM content WHERE status = 1");
            if ($section_result) {
                while ($row = $section_result->fetch_assoc()) {
                    $selected = (isset($_GET['section']) && $row['section'] == $_GET['section']) ? 'selected' : '';
                    echo "<option value='{$row['section']}' {$selected}>{$row['section']}</option>";
                }
            }
            ?>
        </select>
    </form>

    <?php
    $section = isset($_GET['section']) ? mysqli_real_escape_string($conn, $_GET['section']) : '';

    $sql = "SELECT * FROM content WHERE status = 1 ";

    // Filter out internal content
    if ($section == "Internal")
        $section = "";

    if (!empty($section)) {
        $sql .= "AND section = '" . $section . "' ";
    }
    $sql .= "ORDER BY created_at DESC";

    $result = $conn->query($sql);

    if ($result === false) {
        die("Error in query: " . $conn->error);
    }

    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "<div class='content-item'>
                    <h3>{$row['title']}</h3>
                    <span class='section-badge'>{$row['section']}</span>
                    <p>" . substr($row['body'], 0, 200) . "...</p>
                </div>";
        }
    } else {
        echo "<p>No content available.</p>";
    }
    $conn->close();
    ?>
    
    <hr style="margin-top: 30px;">
    <p style="font-size: 0.8em; color: #999;">eZCMS v2.5 | Legacy Authentication System</p>
</div>
</body>
</html>
