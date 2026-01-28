<?php
    header('Content-Type: application/json');
    
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    
    $action = isset($_GET['action']) ? $_GET['action'] : 'info';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        echo json_encode(['error' => 'Database connection failed']);
        exit;
    }
    
    switch ($action) {
        case 'subsites':
            $result = $conn->query("SELECT id, title, domain, is_active FROM subsites");
            $data = [];
            while ($row = $result->fetch_assoc()) {
                $data[] = $row;
            }
            echo json_encode(['status' => 'success', 'data' => $data]);
            break;
            
        case 'groups':
            $type = isset($_GET['type']) ? mysqli_real_escape_string($conn, $_GET['type']) : 'user_groups';
            $allowed = ['user_groups', 'admin_groups', 'content_groups'];
            if (!in_array($type, $allowed)) {
                echo json_encode(['error' => 'Invalid group type']);
                exit;
            }
            $result = $conn->query("SELECT id, name, description, subsite_id FROM `$type`");
            $data = [];
            while ($row = $result->fetch_assoc()) {
                $data[] = $row;
            }
            echo json_encode(['status' => 'success', 'data' => $data]);
            break;
            
        case 'members':
            $result = $conn->query("SELECT id, email, first_name, last_name, is_active FROM members LIMIT 10");
            $data = [];
            while ($row = $result->fetch_assoc()) {
                $data[] = $row;
            }
            echo json_encode(['status' => 'success', 'data' => $data]);
            break;
            
        case 'info':
        default:
            echo json_encode([
                'name' => 'SubSite Manager API',
                'version' => '3.2.1',
                'endpoints' => [
                    '/api.php?action=info' => 'API information',
                    '/api.php?action=subsites' => 'List all subsites',
                    '/api.php?action=groups&type={type}' => 'List groups by type',
                    '/api.php?action=members' => 'List members (limited)'
                ]
            ]);
            break;
    }
    
    $conn->close();
?>
