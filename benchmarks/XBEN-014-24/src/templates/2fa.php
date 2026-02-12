    <div class="container">
        <div class="card" style="max-width: 420px; margin: 60px auto;">
            <h2>Two-Factor Authentication</h2>
            <p style="margin-bottom: 16px; color: #666; font-size: 14px;">
                Enter the 6-digit verification code from your authenticator app to continue.
            </p>
            <?php if (isset($twofa_error)): ?>
                <div class="alert alert-danger"><?php echo htmlspecialchars($twofa_error); ?></div>
            <?php endif; ?>
            <form method="POST" action="/?page=2fa">
                <div class="form-group">
                    <label for="code">Verification Code</label>
                    <input type="text" id="code" name="code" maxlength="6" pattern="[0-9]{6}"
                           placeholder="000000" autocomplete="one-time-code" required
                           style="text-align: center; font-size: 24px; letter-spacing: 8px;">
                </div>
                <button type="submit" class="btn">Verify</button>
            </form>
        </div>
    </div>