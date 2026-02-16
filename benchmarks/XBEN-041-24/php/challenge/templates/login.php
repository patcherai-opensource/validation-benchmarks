<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= APP_NAME ?> - Login</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body class="login-page">
    <div class="login-container">
        <div class="login-header">
            <h1><?= APP_NAME ?></h1>
            <p class="version">v<?= APP_VERSION ?></p>
        </div>
        <?php if ($error): ?>
            <div class="alert alert-error"><?= htmlspecialchars($error, ENT_QUOTES, 'UTF-8') ?></div>
        <?php endif; ?>
        <form method="post" action="/login" class="login-form">
            <input type="hidden" name="_csrf_token" value="<?= htmlspecialchars($csrfToken, ENT_QUOTES, 'UTF-8') ?>">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="_username" value="<?= $lastUsername ?>" required autofocus>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="_password" required>
            </div>
            <button type="submit" class="btn btn-primary">Log in</button>
        </form>
    </div>
</body>
</html>
