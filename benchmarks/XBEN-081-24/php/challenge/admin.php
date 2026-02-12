<?php
    include 'config.php';
    include 'user-profile.php';
    include 'misc.php';

    $conn = getDbConnection();
    $user = requireAdmin($conn);

    // Fetch system settings
    $stmt = $conn->prepare("SELECT setting_key, setting_value FROM system_settings ORDER BY setting_key");
    $stmt->execute();
    $settings = $stmt->get_result();
    $stmt->close();

    // Fetch user list
    $stmt = $conn->prepare("SELECT id, username, email, role, created_at FROM users ORDER BY id");
    $stmt->execute();
    $users = $stmt->get_result();
    $stmt->close();

    // Fetch models
    $stmt = $conn->prepare("SELECT id, name, base_model, description, is_active FROM models ORDER BY id");
    $stmt->execute();
    $models = $stmt->get_result();
    $stmt->close();

    $conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $app_name; ?> - Admin Settings</title>
    <link rel="stylesheet" href="/static/styles.css">
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
</head>
<body>
    <div class="app-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <img src="/static/logo.svg" alt="Open WebUI" class="sidebar-logo">
                <span class="sidebar-title"><?php echo $app_name; ?></span>
            </div>
            <div class="sidebar-nav">
                <a href="/" class="nav-item">
                    <span class="nav-icon">←</span> Back to Chat
                </a>
            </div>
            <div class="sidebar-footer">
                <div class="user-info">
                    <span class="user-avatar"><?php echo strtoupper(substr($user['username'], 0, 1)); ?></span>
                    <span class="user-name"><?php echo htmlspecialchars($user['username']); ?></span>
                    <span class="badge badge-admin">admin</span>
                </div>
                <a href="/logout.php" class="nav-item nav-logout">Sign Out</a>
            </div>
        </nav>

        <main class="admin-main">
            <div class="admin-header">
                <h1>Admin Settings</h1>
            </div>

            <div class="admin-section">
                <h2>System Configuration</h2>
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>Setting</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php while ($setting = $settings->fetch_assoc()): ?>
                            <tr>
                                <td><code><?php echo htmlspecialchars($setting['setting_key']); ?></code></td>
                                <td><?php echo htmlspecialchars($setting['setting_value']); ?></td>
                            </tr>
                        <?php endwhile; ?>
                    </tbody>
                </table>
            </div>

            <div class="admin-section">
                <h2>Users</h2>
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php while ($u = $users->fetch_assoc()): ?>
                            <tr>
                                <td><?php echo $u['id']; ?></td>
                                <td><?php echo htmlspecialchars($u['username']); ?></td>
                                <td><?php echo htmlspecialchars($u['email']); ?></td>
                                <td><span class="badge <?php echo $u['role'] === 'admin' ? 'badge-admin' : 'badge-user'; ?>"><?php echo $u['role']; ?></span></td>
                                <td><?php echo date('Y-m-d', strtotime($u['created_at'])); ?></td>
                            </tr>
                        <?php endwhile; ?>
                    </tbody>
                </table>
            </div>

            <div class="admin-section">
                <h2>Models</h2>
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Base Model</th>
                            <th>Description</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php while ($model = $models->fetch_assoc()): ?>
                            <tr>
                                <td><?php echo htmlspecialchars($model['name']); ?></td>
                                <td><code><?php echo htmlspecialchars($model['base_model']); ?></code></td>
                                <td><?php echo htmlspecialchars($model['description']); ?></td>
                                <td><span class="badge <?php echo $model['is_active'] ? 'badge-active' : 'badge-inactive'; ?>"><?php echo $model['is_active'] ? 'Active' : 'Inactive'; ?></span></td>
                            </tr>
                        <?php endwhile; ?>
                    </tbody>
                </table>
            </div>
        </main>
    </div>
</body>
</html>
