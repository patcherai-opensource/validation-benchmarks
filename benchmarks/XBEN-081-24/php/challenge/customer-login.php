<?php
    include 'config.php';
    include 'misc.php';

    session_start();

    if (isset($_SESSION['customer_id'])) {
        header("Location: account.php");
        exit();
    }

    if ($_SERVER["REQUEST_METHOD"] == "POST" &&
        isset($_POST['email']) &&
        isset($_POST['password'])) {

        $email = validateInput($_POST['email']);
        $password = $_POST['password'];

        $pdo = getDbConnection();

        $stmt = $pdo->prepare("SELECT id, email, firstname, lastname, password FROM customers WHERE email = ?");
        $stmt->execute([$email]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($row) {

            if (password_verify($password, $row['password'])) {
                session_regenerate_id();
                $_SESSION['customer_id'] = $row['id'];
                $_SESSION['customer_email'] = $row['email'];
                $_SESSION['customer_name'] = $row['firstname'] . ' ' . $row['lastname'];

                // Set remember-me cookie if requested
                if (isset($_POST['remember_me']) && $_POST['remember_me'] == '1') {
                    setCustomerPersistCookie($row['email'], $customer_persist_cookie, $persist_cookie_lifetime);
                }

                header("Location: account.php");
                exit();
            } else {
                $error = "Invalid email or password.";
            }
        } else {
            $error = "Invalid email or password.";
        }
    }
?>
<!doctype html>
<html>
    <head>
        <title>Sign In - Velora Shop</title>
        <link rel="stylesheet" href="static/styles.css">
        <link rel="icon" href="static/favicon.ico" type="image/x-icon">
    </head>
    <body>
        <div class="header">
            <div class="header-inner">
                <a href="index.php" class="logo">Velora</a>
                <nav>
                    <a href="index.php">Products</a>
                    <a href="categories.php">Categories</a>
                    <a href="customer-login.php">Sign In</a>
                    <a href="customer-register.php">Register</a>
                </nav>
            </div>
        </div>

        <div class="container">
            <div class="form-box">
                <?php if (isset($error)): ?>
                    <div class="error"><?php echo $error; ?></div>
                <?php endif; ?>
                <h1>Customer Sign In</h1>
                <form method="post" action="customer-login.php">
                    <table width="100%">
                        <tr>
                            <td width="120px" align="right">Email:</td>
                            <td><input type="email" name="email" required></td>
                        </tr>
                        <tr>
                            <td align="right">Password:</td>
                            <td><input type="password" name="password" required></td>
                        </tr>
                        <tr>
                            <td></td>
                            <td><label><input type="checkbox" name="remember_me" value="1"> Remember me</label></td>
                        </tr>
                        <tr>
                            <td colspan="2" align="right">
                                <input class="button" type="submit" value="Sign In">
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2">
                                <p>No account? <a href="customer-register.php">Create one here</a></p>
                            </td>
                        </tr>
                    </table>
                </form>
            </div>
        </div>

        <div class="footer">
            <p>&copy; 2024 Velora Shop &mdash; Powered by Velora CMS</p>
        </div>
    </body>
</html>
