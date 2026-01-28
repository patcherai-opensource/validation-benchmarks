<?php
/**
 * TaskFlow Portal - Team Page
 */
session_start();

$authenticated_user = $_SESSION['user'] ?? null;

$team_members = [
    ['name' => 'Administrator', 'role' => 'System Admin', 'status' => 'online'],
    ['name' => 'Guest User', 'role' => 'Viewer', 'status' => 'offline'],
    ['name' => 'Demo User', 'role' => 'Team Member', 'status' => 'away']
];
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Team - TaskFlow Portal</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .navbar {
            background: rgba(0,0,0,0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo { font-size: 24px; font-weight: bold; color: #00d4ff; }
        .nav-links a { color: #e0e0e0; text-decoration: none; margin-left: 20px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 30px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .team-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
        .member-card { background: rgba(0,0,0,0.2); padding: 20px; border-radius: 8px; text-align: center; }
        .status-online { color: #0f0; }
        .status-offline { color: #666; }
        .status-away { color: #ff0; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">📊 TaskFlow Portal</div>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/projects.php">Projects</a>
            <a href="/team.php">Team</a>
            <a href="/settings.php">Settings</a>
        </div>
    </nav>
    <div class="container">
        <div class="card">
            <h2>Team Members</h2>
            <div class="team-grid">
                <?php foreach ($team_members as $member): ?>
                    <div class="member-card">
                        <h3><?php echo htmlspecialchars($member['name']); ?></h3>
                        <p style="color: #888;"><?php echo htmlspecialchars($member['role']); ?></p>
                        <p class="status-<?php echo $member['status']; ?>">● <?php echo ucfirst($member['status']); ?></p>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </div>
</body>
</html>
