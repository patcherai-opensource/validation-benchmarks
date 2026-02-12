<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="<?php echo htmlspecialchars($csrfToken ?? ''); ?>">
    <title><?php echo isset($pageTitle) ? htmlspecialchars($pageTitle) . ' - ' : ''; ?>TaskFlow</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #333; min-height: 100vh; }
        .navbar { background: #1a1a2e; padding: 0 2rem; height: 60px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .navbar-brand { color: #e94560; font-size: 1.4rem; font-weight: 700; text-decoration: none; letter-spacing: -0.5px; }
        .navbar-brand span { color: #fff; font-weight: 300; }
        .navbar-nav { display: flex; align-items: center; gap: 1.5rem; list-style: none; }
        .navbar-nav a { color: #a0a0b0; text-decoration: none; font-size: 0.9rem; transition: color 0.2s; }
        .navbar-nav a:hover, .navbar-nav a.active { color: #fff; }
        .navbar-user { display: flex; align-items: center; gap: 0.75rem; }
        .navbar-user .avatar { width: 32px; height: 32px; border-radius: 50%; background: #e94560; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 0.8rem; font-weight: 600; }
        .navbar-user span { color: #d0d0e0; font-size: 0.85rem; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .card { background: #fff; border-radius: 8px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 1.5rem; }
        .card h2 { font-size: 1.1rem; margin-bottom: 1rem; color: #1a1a2e; }
        .btn { display: inline-flex; align-items: center; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.85rem; font-weight: 500; text-decoration: none; cursor: pointer; border: none; transition: all 0.2s; }
        .btn-primary { background: #e94560; color: #fff; }
        .btn-primary:hover { background: #c73652; }
        .btn-secondary { background: #eee; color: #333; }
        .btn-secondary:hover { background: #ddd; }
        .btn-sm { padding: 0.3rem 0.7rem; font-size: 0.8rem; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #eee; }
        th { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; color: #888; font-weight: 600; }
        .badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; }
        .badge-pending { background: #fff3cd; color: #856404; }
        .badge-progress { background: #cce5ff; color: #004085; }
        .badge-completed { background: #d4edda; color: #155724; }
        .badge-critical { background: #f8d7da; color: #721c24; }
        .badge-high { background: #ffe0b2; color: #e65100; }
        .badge-medium { background: #fff9c4; color: #f57f17; }
        .badge-low { background: #e8f5e9; color: #2e7d32; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
        .stat-card { background: #fff; border-radius: 8px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        .stat-card .label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; color: #888; margin-bottom: 0.5rem; }
        .stat-card .value { font-size: 1.8rem; font-weight: 700; color: #1a1a2e; }
        .stat-card .change { font-size: 0.75rem; color: #2e7d32; margin-top: 0.25rem; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 0.4rem; color: #555; }
        .form-control { width: 100%; padding: 0.6rem 0.8rem; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9rem; transition: border-color 0.2s; }
        .form-control:focus { outline: none; border-color: #e94560; box-shadow: 0 0 0 3px rgba(233,69,96,0.1); }
        .alert { padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 1rem; font-size: 0.85rem; }
        .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .footer { text-align: center; padding: 2rem; color: #888; font-size: 0.8rem; }
    </style>
</head>
<body>