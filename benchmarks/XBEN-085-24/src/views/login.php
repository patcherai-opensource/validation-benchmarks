<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - <?= htmlspecialchars($data['appName']) ?></title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f6fa; color: #2d3436; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .login-box { background: #fff; border-radius: 8px; padding: 2rem; width: 100%; max-width: 400px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .login-box h1 { font-size: 1.3rem; margin-bottom: 0.5rem; text-align: center; }
        .login-box p.subtitle { text-align: center; color: #636e72; margin-bottom: 1.5rem; font-size: 0.9rem; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.3rem; font-size: 0.85rem; color: #636e72; }
        .form-group input { width: 100%; padding: 0.6rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.95rem; }
        .form-group input:focus { outline: none; border-color: #74b9ff; }
        .btn { width: 100%; padding: 0.7rem; background: #0984e3; color: #fff; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; }
        .btn:hover { background: #0770c2; }
        .error { background: #ffeaa7; color: #d63031; padding: 0.5rem; border-radius: 4px; margin-bottom: 1rem; font-size: 0.85rem; text-align: center; }
        .back-link { text-align: center; margin-top: 1rem; }
        .back-link a { color: #636e72; font-size: 0.85rem; text-decoration: none; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1><?= htmlspecialchars($data['appName']) ?></h1>
        <p class="subtitle">Sign in to your account</p>
        <?php if (!empty($data['error'])): ?>
            <div class="error"><?= htmlspecialchars($data['error']) ?></div>
        <?php endif; ?>
        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" autocomplete="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" autocomplete="current-password" required>
            </div>
            <button type="submit" class="btn">Sign In</button>
        </form>
        <div class="back-link">
            <a href="/">&larr; Back to Dashboard</a>
        </div>
    </div>
</body>
</html>
