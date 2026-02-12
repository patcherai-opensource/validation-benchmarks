<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($pageTitle ?? APP_NAME) ?> - <?= APP_NAME ?></title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f4f6f9;
            color: #333;
            line-height: 1.6;
        }
        .navbar {
            background-color: #1a237e;
            color: #fff;
            padding: 0 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 56px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .navbar .brand {
            font-size: 18px;
            font-weight: 600;
            text-decoration: none;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .navbar .brand svg { width: 24px; height: 24px; fill: #fff; }
        .navbar nav { display: flex; gap: 4px; }
        .navbar nav a {
            color: rgba(255,255,255,0.8);
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            transition: background-color 0.2s;
        }
        .navbar nav a:hover, .navbar nav a.active {
            background-color: rgba(255,255,255,0.1);
            color: #fff;
        }
        .navbar .user-info {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
        }
        .navbar .user-info .avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background-color: #3949ab;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 14px;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 24px; }
        .card {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            padding: 24px;
            margin-bottom: 16px;
        }
        .card h2 { margin-bottom: 16px; font-size: 20px; color: #1a237e; }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            transition: background-color 0.2s;
        }
        .btn-primary { background-color: #1a237e; color: #fff; }
        .btn-primary:hover { background-color: #283593; }
        .btn-danger { background-color: #c62828; color: #fff; }
        .btn-danger:hover { background-color: #d32f2f; }
        .btn-secondary { background-color: #e0e0e0; color: #333; }
        .btn-secondary:hover { background-color: #bdbdbd; }
        .alert { padding: 12px 16px; border-radius: 4px; margin-bottom: 16px; font-size: 14px; }
        .alert-danger { background-color: #ffebee; color: #c62828; border: 1px solid #ef9a9a; }
        .alert-success { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
        .alert-info { background-color: #e3f2fd; color: #1565c0; border: 1px solid #90caf9; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; margin-bottom: 4px; font-weight: 500; font-size: 14px; color: #555; }
        .form-group input[type="text"],
        .form-group input[type="password"] {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        .form-group input:focus { outline: none; border-color: #1a237e; box-shadow: 0 0 0 2px rgba(26,35,126,0.1); }
        .checkbox-group { display: flex; align-items: center; gap: 8px; }
        .checkbox-group input[type="checkbox"] { width: 16px; height: 16px; }
        .checkbox-group label { font-weight: 400; }
        table { width: 100%; border-collapse: collapse; }
        table th, table td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; }
        table th { font-weight: 600; color: #555; background-color: #fafafa; }
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge-success { background-color: #e8f5e9; color: #2e7d32; }
        .badge-warning { background-color: #fff3e0; color: #e65100; }
        .badge-info { background-color: #e3f2fd; color: #1565c0; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
        .stat-card { text-align: center; }
        .stat-card .stat-value { font-size: 36px; font-weight: 700; color: #1a237e; }
        .stat-card .stat-label { font-size: 14px; color: #888; margin-top: 4px; }
        footer { text-align: center; padding: 20px; color: #999; font-size: 12px; }
    </style>
</head>
<body>
