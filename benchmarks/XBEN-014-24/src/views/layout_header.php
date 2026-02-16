<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($pageTitle ?? 'SecurePortal') ?></title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f0f2f5;
            color: #1a1a2e;
            min-height: 100vh;
        }
        .navbar {
            background: #1a1a2e;
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 56px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .navbar .brand {
            color: #e94560;
            font-weight: 700;
            font-size: 1.1rem;
            text-decoration: none;
            letter-spacing: 0.5px;
        }
        .navbar .nav-links {
            display: flex;
            gap: 1.5rem;
            align-items: center;
        }
        .navbar .nav-links a {
            color: #a0a0b8;
            text-decoration: none;
            font-size: 0.9rem;
            transition: color 0.2s;
        }
        .navbar .nav-links a:hover { color: #fff; }
        .navbar .nav-links a.active { color: #e94560; }
        .container {
            max-width: 960px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }
        .card {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            padding: 2rem;
            margin-bottom: 1.5rem;
        }
        .card h2 {
            margin-bottom: 1rem;
            color: #1a1a2e;
            font-size: 1.3rem;
        }
        .form-group {
            margin-bottom: 1rem;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.4rem;
            font-weight: 500;
            color: #444;
            font-size: 0.9rem;
        }
        .form-group input[type="text"],
        .form-group input[type="password"],
        .form-group input[type="email"] {
            width: 100%;
            padding: 0.6rem 0.8rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.95rem;
            transition: border-color 0.2s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #e94560;
        }
        .checkbox-group {
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .checkbox-group label {
            font-size: 0.9rem;
            color: #666;
            cursor: pointer;
        }
        .btn {
            display: inline-block;
            padding: 0.6rem 1.5rem;
            background: #e94560;
            color: #fff;
            border: none;
            border-radius: 4px;
            font-size: 0.95rem;
            cursor: pointer;
            text-decoration: none;
            transition: background 0.2s;
        }
        .btn:hover { background: #c73550; }
        .btn-secondary {
            background: #6c757d;
        }
        .btn-secondary:hover { background: #5a6268; }
        .alert {
            padding: 0.8rem 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table th, table td {
            padding: 0.6rem 0.8rem;
            text-align: left;
            border-bottom: 1px solid #eee;
            font-size: 0.9rem;
        }
        table th {
            font-weight: 600;
            color: #666;
            background: #fafafa;
        }
        .badge {
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 3px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-admin { background: #e94560; color: #fff; }
        .badge-user { background: #6c757d; color: #fff; }
        .badge-enabled { background: #28a745; color: #fff; }
        .badge-disabled { background: #dc3545; color: #fff; }
        .auth-container {
            max-width: 420px;
            margin: 4rem auto;
            padding: 0 1rem;
        }
        .auth-card {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            padding: 2.5rem;
        }
        .auth-card .logo {
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .auth-card .logo h1 {
            color: #e94560;
            font-size: 1.5rem;
            letter-spacing: 0.5px;
        }
        .auth-card .logo p {
            color: #888;
            font-size: 0.85rem;
            margin-top: 0.3rem;
        }
        .note-content {
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 4px;
            border-left: 3px solid #e94560;
            margin: 0.5rem 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            word-break: break-all;
        }
        .footer {
            text-align: center;
            padding: 2rem;
            color: #999;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
