document.addEventListener('DOMContentLoaded', function() {
    var loginLink = document.getElementById('login-link');
    var loginModal = document.getElementById('login-modal');
    var loginCancel = document.getElementById('login-cancel');
    var loginForm = document.getElementById('login-form');
    var loginError = document.getElementById('login-error');

    loginLink.addEventListener('click', function(e) {
        e.preventDefault();
        loginModal.style.display = 'block';
    });

    loginCancel.addEventListener('click', function() {
        loginModal.style.display = 'none';
        loginError.style.display = 'none';
    });

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        var username = document.getElementById('login-username').value;
        var password = document.getElementById('login-password').value;

        fetch('/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: username, password: password})
        }).then(function(r) { return r.json(); }).then(function(data) {
            if (data.error) {
                loginError.textContent = data.error;
                loginError.style.display = 'block';
            } else {
                loginModal.style.display = 'none';
                document.getElementById('username-display').textContent = data.username + ' (' + data.role + ')';
                loginLink.textContent = 'Logout';
            }
        }).catch(function() {
            loginError.textContent = 'Connection error';
            loginError.style.display = 'block';
        });
    });
});