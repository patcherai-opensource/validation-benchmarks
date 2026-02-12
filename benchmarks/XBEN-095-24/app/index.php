<?php
/**
 * Teampass - a collaborative passwords manager
 *
 * This file is the main entry point for the application.
 */

session_start();

require_once __DIR__ . '/includes/config.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Teampass - Collaborative Passwords Manager</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        body { background-color: #f5f5f5; }
        .login-container {
            max-width: 420px;
            margin: 80px auto;
            padding: 30px;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .login-header h2 {
            color: #2c3e50;
            font-weight: 600;
        }
        .login-header p {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .version-info {
            text-align: center;
            color: #bdc3c7;
            font-size: 0.75em;
            margin-top: 20px;
        }
        .btn-teampass {
            background-color: #2980b9;
            border-color: #2980b9;
            color: #fff;
        }
        .btn-teampass:hover {
            background-color: #2471a3;
            border-color: #2471a3;
            color: #fff;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h2><i class="fas fa-lock"></i> Teampass</h2>
            <p>Collaborative Passwords Manager</p>
        </div>

        <?php if (isset($_SESSION['error'])): ?>
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <?php echo htmlspecialchars($_SESSION['error']); unset($_SESSION['error']); ?>
                <button type="button" class="close" data-dismiss="alert"><span>&times;</span></button>
            </div>
        <?php endif; ?>

        <?php if (isset($_SESSION['success'])): ?>
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <?php echo htmlspecialchars($_SESSION['success']); unset($_SESSION['success']); ?>
                <button type="button" class="close" data-dismiss="alert"><span>&times;</span></button>
            </div>
        <?php endif; ?>

        <form action="/sources/identify.php" method="POST">
            <div class="form-group">
                <label for="login"><i class="fas fa-user"></i> Login</label>
                <input type="text" class="form-control" id="login" name="login" placeholder="Your login" required>
            </div>
            <div class="form-group">
                <label for="pw"><i class="fas fa-key"></i> Password</label>
                <input type="password" class="form-control" id="pw" name="pw" placeholder="Your password" required>
            </div>
            <div class="form-group form-check">
                <input type="checkbox" class="form-check-input" id="duocheck">
                <label class="form-check-label" for="duocheck">Use Duo Security</label>
            </div>
            <button type="submit" class="btn btn-teampass btn-block">
                <i class="fas fa-sign-in-alt"></i> Connect
            </button>
        </form>

        <div class="version-info">
            Teampass <?php echo TP_VERSION; ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>