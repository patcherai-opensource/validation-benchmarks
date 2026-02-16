<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars(isset($title) ? $title . ' - Meridian Platform' : 'Meridian Platform'); ?></title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #f5f6fa; color: #2c3e50; line-height: 1.6; }
        .navbar { background: #2c3e50; color: #ecf0f1; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; height: 56px; }
        .navbar .brand { font-size: 18px; font-weight: 600; letter-spacing: 0.5px; }
        .navbar .brand span { color: #3498db; }
        .navbar .nav-links { display: flex; gap: 16px; align-items: center; }
        .navbar .nav-links a { color: #bdc3c7; text-decoration: none; font-size: 14px; padding: 8px 12px; border-radius: 4px; transition: background 0.2s; }
        .navbar .nav-links a:hover { background: #34495e; color: #ecf0f1; }
        .navbar .nav-links a.active { color: #3498db; }
        .navbar .user-info { font-size: 13px; color: #95a5a6; }
        .container { max-width: 1100px; margin: 32px auto; padding: 0 24px; }
        .card { background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); padding: 24px; margin-bottom: 20px; }
        .card h2 { font-size: 20px; margin-bottom: 12px; color: #2c3e50; }
        .card h3 { font-size: 16px; margin-bottom: 8px; color: #34495e; }
        .card p { color: #7f8c8d; font-size: 14px; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-warning { background: #fff3cd; color: #856404; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        .badge-info { background: #d1ecf1; color: #0c5460; }
        .btn { display: inline-block; padding: 8px 20px; border-radius: 4px; border: none; cursor: pointer; font-size: 14px; text-decoration: none; transition: background 0.2s; }
        .btn-primary { background: #3498db; color: #fff; }
        .btn-primary:hover { background: #2980b9; }
        .btn-danger { background: #e74c3c; color: #fff; }
        .btn-danger:hover { background: #c0392b; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 14px; color: #34495e; }
        .form-group input { width: 100%; padding: 10px 12px; border: 1px solid #dce1e8; border-radius: 4px; font-size: 14px; }
        .form-group input:focus { outline: none; border-color: #3498db; box-shadow: 0 0 0 3px rgba(52,152,219,0.15); }
        .alert { padding: 12px 16px; border-radius: 4px; margin-bottom: 16px; font-size: 14px; }
        .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .alert-info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        table { width: 100%; border-collapse: collapse; }
        table th, table td { padding: 10px 14px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; }
        table th { background: #f8f9fa; font-weight: 600; color: #34495e; }
        .sidebar-layout { display: flex; gap: 24px; }
        .sidebar { width: 220px; flex-shrink: 0; }
        .sidebar a { display: block; padding: 10px 14px; color: #34495e; text-decoration: none; border-radius: 4px; font-size: 14px; margin-bottom: 2px; }
        .sidebar a:hover { background: #edf2f7; }
        .sidebar a.active { background: #3498db; color: #fff; }
        .main-content { flex: 1; }
        .config-block { background: #f8f9fa; border: 1px solid #e2e8f0; border-radius: 4px; padding: 16px; font-family: 'Courier New', monospace; font-size: 13px; white-space: pre-wrap; word-break: break-all; color: #2d3748; }
        .footer { text-align: center; padding: 24px; color: #95a5a6; font-size: 12px; }
    </style>
</head>
<body>
