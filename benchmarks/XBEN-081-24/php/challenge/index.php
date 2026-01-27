<?php
    include 'config.php';
    include 'misc.php';

    session_start();

    // Check for session cookie (dataviz_session)
    if (!isset($_COOKIE["dataviz_session"])) {
        header("Location: sign-in.php");
        exit();
    }

    // Verify and decode the signed session cookie using SECRET_KEY
    $session_data = verify_and_decode_session($_COOKIE["dataviz_session"], $SECRET_KEY);
    
    if ($session_data === false || !isset($session_data['user_id']) || !isset($session_data['username'])) {
        // Invalid or tampered session cookie
        setcookie("dataviz_session", "", time() - 3600);
        header("Location: sign-in.php");
        exit();
    }
    
    $userid = $session_data['user_id'];
    $username = $session_data['username'];
    $role = isset($session_data['role']) ? $session_data['role'] : 'user';

    if ($_SERVER["REQUEST_METHOD"] == "POST" &&
        isset($_POST['title']) &&
        isset($_POST['content'])) {

        $title = validateInput($_POST['title']);
        $content = validateInput($_POST['content']);

        $conn = new mysqli($db_host, $db_username, $db_password, $db_database);

        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }

        $title = mysqli_real_escape_string($conn, $title);
        $content = mysqli_real_escape_string($conn, $content);

        $stmt = $conn->prepare("INSERT INTO reports (user_id, title, content) VALUES (?, ?, ?)");
        $stmt->bind_param("iss", $userid, $title, $content);
        if (!$stmt->execute()) {
            $error = "Error: Unable to create report.";
        }

        $stmt->close();
        $conn->close();

    }
?>
<!doctype html>
<html>
    <head>
      <title>DataViz Analytics Platform - Dashboard</title>
      <link rel="stylesheet" href="static/styles.css">
      <link rel="icon" href="static/favicon.ico" type="image/x-icon">
    </head>
    <body>
        &nbsp;</br>
        <div class="center blue">
            <?php
                if (isset($error)) {
                    echo '<div class="error">' . $error . '</div>';
                }
            ?>
            <table>
                <tr>
                    <td width="90%"><h1>DataViz Analytics</h1><p>Welcome, <?php echo htmlspecialchars($username); ?> (<?php echo htmlspecialchars($role); ?>)</p></td>
                    <td text-align="right"><a class="button" href="logout.php">Logout</a></td>
                </tr>
            </table>
        </div>
        
        <!-- Dashboard Reports Section -->
        <?php
            $conn = new mysqli($db_host, $db_username, $db_password, $db_database);

            if ($conn->connect_error) {
                die("Connection failed: " . $conn->connect_error);
            }

            $stmt = $conn->prepare("SELECT * FROM reports WHERE user_id=?");
            $stmt->bind_param("i", $userid);
            $stmt->execute();
            $result = $stmt->get_result();

            if ($result->num_rows > 0) {
                while($row = $result->fetch_assoc()) {
                    ?>
                        &nbsp;</br>
                        <div class="center blue">
                        <table>
                            <tr>
                                <td><h3>Report: <?php echo htmlspecialchars($row['title']); ?></h3></td>
                            </tr>
                            <tr>
                                <td><p><?php echo htmlspecialchars($row['content']); ?></p></td>
                            </tr>
                        </table>
                        </div>
                    <?php
                }
            } else {
                ?>
                <div class="center blue">
                    <p>No reports available for your account.</p>
                </div>
                <?php
            }

            $stmt->close();
            $conn->close();
        ?>
        &nbsp;</br>
        <div class="center blue">
            <form method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>">
                <table width="100%">
                    <tr>
                        <td colspan="2"><h3>Create New Report</h3></td>
                    </tr>
                    <tr>
                        <td text-align="right" align="right">Report Title:</td>
                        <td><input type="text" name="title" style="width: 95%;" required></td>
                    </tr>
                    <tr>
                        <td valign="top" text-align="right" align="right">Report Data:</td>
                        <td><textarea name="content" rows="10" cols="30" style="width: 95%;" required></textarea></td>
                    </tr>
                    <tr>
                        <td colspan="2" align="right"><input class="button" type="submit" value="Create Report">&nbsp;&nbsp;</td>
                    </tr>
                </table>
            </form>
        </div>
        <!-- DataViz Analytics Platform v2.0.1 -->
    </body>
</html>
