<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log in - Akeneo PIM</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Lato', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #11324d; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .login-container { background: #fff; border-radius: 8px; padding: 48px 40px; width: 380px; box-shadow: 0 8px 40px rgba(0,0,0,0.2); }
        .logo { text-align: center; margin-bottom: 36px; font-size: 28px; font-weight: 700; color: #11324d; }
        .logo span { color: #9452ba; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; font-size: 12px; text-transform: uppercase; letter-spacing: 0.8px; color: #67768b; margin-bottom: 6px; }
        .form-group input { width: 100%; padding: 10px 14px; border: 1px solid #d4d6dc; border-radius: 4px; font-size: 14px; color: #11324d; outline: none; transition: border-color 0.2s; }
        .form-group input:focus { border-color: #9452ba; }
        .btn-login { width: 100%; padding: 12px; background: #9452ba; color: #fff; border: none; border-radius: 4px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
        .btn-login:hover { background: #7d3fa6; }
        .error-msg { background: #fde8e8; color: #c91c1c; padding: 10px 14px; border-radius: 4px; font-size: 13px; margin-bottom: 20px; }
        .version { text-align: center; margin-top: 24px; font-size: 11px; color: #a1b1c2; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo"><span>akeneo</span> PIM</div>
        <?php if (!empty($error)): ?>
            <div class="error-msg"><?= htmlspecialchars($error) ?></div>
        <?php endif; ?>
        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="_username" autocomplete="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="_password" autocomplete="current-password" required>
            </div>
            <button type="submit" class="btn-login">Log in</button>
        </form>
        <div class="version">Community Edition v5.0.118</div>
    </div>
</body>
</html>