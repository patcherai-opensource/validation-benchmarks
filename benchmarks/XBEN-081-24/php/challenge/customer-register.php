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
        isset($_POST['password']) &&
        isset($_POST['firstname']) &&
        isset($_POST['lastname'])) {

        $email = validateInput($_POST['email']);
        $firstname = validateInput($_POST['firstname']);
        $lastname = validateInput($_POST['lastname']);
        $password = $_POST['password'];

        $pdo = getDbConnection();

        $password_hash = password_hash($password, PASSWORD_DEFAULT);

        try {
            $stmt = $pdo->prepare("INSERT INTO customers (email, password, firstname, lastname) VALUES (?, ?, ?, ?)");
            $stmt->execute([$email, $password_hash, $firstname, $lastname]);
            header("Location: customer-login.php");
            exit();
        } catch (PDOException $e) {
            $error = "Registration failed. Email may already be in use.";
        }
    }
?>
<!doctype html>
<html>
    <head>
        <title>Register - Velora Shop</title>
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
                <h1>Create Customer Account</h1>
                <form method="post" action="customer-register.php">
                    <table width="100%">
                        <tr>
                            <td width="120px" align="right">First Name:</td>
                            <td><input type="text" name="firstname" required></td>
                        </tr>
                        <tr>
                            <td align="right">Last Name:</td>
                            <td><input type="text" name="lastname" required></td>
                        </tr>
                        <tr>
                            <td align="right">Email:</td>
                            <td><input type="email" name="email" required></td>
                        </tr>
                        <tr>
                            <td align="right">Password:</td>
                            <td><input type="password" name="password" required></td>
                        </tr>
                        <tr>
                            <td colspan="2" align="right">
                                <input class="button" type="submit" value="Register">
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2">
                                <p>Already have an account? <a href="customer-login.php">Sign in</a></p>
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
