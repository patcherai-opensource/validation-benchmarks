<?php include __DIR__ . '/_header.php'; ?>
<div class="security-page">
    <div class="brand-header">
        <h1>Corporate Portal</h1>
        <p class="tagline">Internal Management System</p>
    </div>
    <div class="security-form-container">
        <h2>Password Reset</h2>
        <p>A password reset link has been sent to <strong><?= $email ?></strong>, provided an account exists for that email address.</p>
        <p>Please check your inbox and follow the instructions to reset your password.</p>
        <p><a href="/Account/signin">&larr; Back to login</a></p>
    </div>
</div>
<?php include __DIR__ . '/_footer.php'; ?>
