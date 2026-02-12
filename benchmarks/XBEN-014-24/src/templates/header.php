<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo APP_NAME; ?></title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f7fa;
            color: #333;
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #1a237e, #283593);
            color: #fff;
            padding: 0 24px;
            height: 56px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .navbar .brand {
            font-size: 18px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .navbar .nav-links a {
            color: rgba(255,255,255,0.85);
            text-decoration: none;
            margin-left: 20px;
            font-size: 14px;
            transition: color 0.2s;
        }
        .navbar .nav-links a:hover { color: #fff; }
        .container {
            max-width: 960px;
            margin: 40px auto;
            padding: 0 20px;
        }
        .card {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            padding: 32px;
            margin-bottom: 24px;
        }
        .card h2 {
            font-size: 22px;
            margin-bottom: 16px;
            color: #1a237e;
        }
        .form-group { margin-bottom: 16px; }
        .form-group label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 6px;
            color: #555;
        }
        .form-group input[type="text"],
        .form-group input[type="password"] {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #1a237e;
        }
        .form-group-inline {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 16px;
        }
        .form-group-inline label {
            font-size: 13px;
            color: #666;
            margin: 0;
        }
        .btn {
            display: inline-block;
            padding: 10px 24px;
            background: #1a237e;
            color: #fff;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
            text-decoration: none;
        }
        .btn:hover { background: #283593; }
        .btn-secondary {
            background: #78909c;
        }
        .btn-secondary:hover { background: #607d8b; }
        .alert {
            padding: 12px 16px;
            border-radius: 4px;
            margin-bottom: 16px;
            font-size: 14px;
        }
        .alert-danger {
            background: #ffeef0;
            color: #c62828;
            border: 1px solid #ffcdd2;
        }
        .alert-info {
            background: #e3f2fd;
            color: #1565c0;
            border: 1px solid #bbdefb;
        }
        .alert-success {
            background: #e8f5e9;
            color: #2e7d32;
            border: 1px solid #c8e6c9;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: #fff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            text-align: center;
        }
        .stat-card .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: #1a237e;
        }
        .stat-card .stat-label {
            font-size: 13px;
            color: #888;
            margin-top: 4px;
        }
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        .data-table th,
        .data-table td {
            padding: 10px 14px;
            text-align: left;
            border-bottom: 1px solid #eee;
            font-size: 14px;
        }
        .data-table th {
            background: #f5f7fa;
            font-weight: 600;
            color: #555;
        }
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge-success { background: #e8f5e9; color: #2e7d32; }
        .badge-warning { background: #fff3e0; color: #e65100; }
        .badge-info { background: #e3f2fd; color: #1565c0; }
        .footer {
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="brand"><?php echo APP_NAME; ?></div>
        <div class="nav-links">
            <?php if (isset($_SESSION['user_id']) && (!isset($_SESSION['2fa_pending']) || !$_SESSION['2fa_pending'])): ?>
                <a href="/?page=dashboard">Dashboard</a>
                <a href="/?page=settings">Settings</a>
                <a href="/?page=logout">Logout</a>
            <?php else: ?>
                <a href="/?page=login">Sign In</a>
            <?php endif; ?>
        </div>
    </div>