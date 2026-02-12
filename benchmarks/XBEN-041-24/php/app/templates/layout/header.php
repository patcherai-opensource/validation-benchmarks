<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($pageTitle ?? 'Akeneo PIM') ?></title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Lato', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f6f7fb; color: #11324d; }

        .topbar { background: #11324d; color: #fff; padding: 0 24px; height: 54px; display: flex; align-items: center; justify-content: space-between; }
        .topbar .logo { font-size: 18px; font-weight: 700; letter-spacing: 0.5px; }
        .topbar .logo span { color: #9452ba; }
        .topbar .user-info { font-size: 13px; display: flex; align-items: center; gap: 16px; }
        .topbar .user-info a { color: #a1b1c2; text-decoration: none; font-size: 12px; }
        .topbar .user-info a:hover { color: #fff; }

        .sidebar { position: fixed; left: 0; top: 54px; bottom: 0; width: 220px; background: #fff; border-right: 1px solid #e1e3e9; padding: 20px 0; overflow-y: auto; }
        .sidebar a { display: block; padding: 10px 24px; color: #67768b; text-decoration: none; font-size: 13px; border-left: 3px solid transparent; }
        .sidebar a:hover, .sidebar a.active { color: #9452ba; background: #f9f0ff; border-left-color: #9452ba; }
        .sidebar .section-title { font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: #a1b1c2; padding: 20px 24px 6px; }

        .main { margin-left: 220px; padding: 32px 40px; min-height: calc(100vh - 54px); }
        .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
        .page-header h1 { font-size: 24px; font-weight: 400; }

        table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 4px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        table th { background: #f6f7fb; font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; color: #67768b; text-align: left; padding: 12px 16px; border-bottom: 1px solid #e1e3e9; }
        table td { padding: 12px 16px; border-bottom: 1px solid #f0f1f5; font-size: 14px; }
        table tr:hover { background: #fafbfd; }

        .btn { display: inline-block; padding: 8px 20px; border-radius: 4px; font-size: 13px; font-weight: 600; text-decoration: none; cursor: pointer; border: none; }
        .btn-primary { background: #9452ba; color: #fff; }
        .btn-primary:hover { background: #7d3fa6; }
        .btn-secondary { background: #e1e3e9; color: #11324d; }

        .badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
        .badge-success { background: #e6f9e8; color: #1d8a2e; }
        .badge-warning { background: #fff8e6; color: #b58105; }
        .badge-danger { background: #fde8e8; color: #c91c1c; }

        .progress-bar { width: 100%; height: 6px; background: #e1e3e9; border-radius: 3px; overflow: hidden; }
        .progress-bar .fill { height: 100%; background: #9452ba; border-radius: 3px; }

        .card { background: #fff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); padding: 24px; margin-bottom: 20px; }

        .upload-area { border: 2px dashed #d4d6dc; border-radius: 8px; padding: 40px; text-align: center; margin: 20px 0; }
        .upload-area:hover { border-color: #9452ba; }

        .media-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; margin-top: 20px; }
        .media-item { background: #fff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); overflow: hidden; }
        .media-item img { width: 100%; height: 140px; object-fit: cover; }
        .media-item .meta { padding: 10px; font-size: 12px; color: #67768b; word-break: break-all; }

        .stat-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 32px; }
        .stat-card { background: #fff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); padding: 20px; }
        .stat-card .number { font-size: 32px; font-weight: 700; color: #9452ba; }
        .stat-card .label { font-size: 12px; color: #67768b; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="topbar">
        <div class="logo"><span>akeneo</span> PIM</div>
        <div class="user-info">
            <span><?= htmlspecialchars($user['first_name'] . ' ' . $user['last_name']) ?></span>
            <a href="/logout">Sign out</a>
        </div>
    </div>
    <div class="sidebar">
        <div class="section-title">Activity</div>
        <a href="/dashboard" class="<?= ($currentPage ?? '') === 'dashboard' ? 'active' : '' ?>">Dashboard</a>

        <div class="section-title">Enrich</div>
        <a href="/enrich/products" class="<?= ($currentPage ?? '') === 'products' ? 'active' : '' ?>">Products</a>
        <a href="/enrich/categories" class="<?= ($currentPage ?? '') === 'categories' ? 'active' : '' ?>">Categories</a>

        <div class="section-title">Collect</div>
        <a href="/collect/channels" class="<?= ($currentPage ?? '') === 'channels' ? 'active' : '' ?>">Channels</a>

        <div class="section-title">Settings</div>
        <a href="/settings/locales" class="<?= ($currentPage ?? '') === 'locales' ? 'active' : '' ?>">Locales</a>
    </div>
    <div class="main">