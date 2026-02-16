document.addEventListener('DOMContentLoaded', function() {
    var container = document.getElementById('cameras-container');
    var loginOverlay = document.getElementById('login-overlay');
    var loginLink = document.getElementById('login-link');
    var settingsLink = document.getElementById('settings-link');
    var loginBtn = document.getElementById('login-btn');
    var loginError = document.getElementById('login-error');

    function loadCameras() {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/settings/cameras', true);
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.onload = function() {
            if (xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);
                renderCameras(data.cameras || []);
            } else if (xhr.status === 403) {
                container.innerHTML = '<div class="camera-card"><div class="camera-preview">Authentication required</div><div class="camera-info"><h3>Please login</h3><div class="meta">Camera listing requires authentication</div></div></div>';
            }
        };
        xhr.onerror = function() {
            container.innerHTML = '<div class="camera-card"><div class="camera-preview">Connection error</div></div>';
        };
        xhr.send();
    }

    function renderCameras(cameras) {
        container.innerHTML = '';
        cameras.forEach(function(cam) {
            var card = document.createElement('div');
            card.className = 'camera-card';
            var statusClass = cam.enabled ? 'status-online' : 'status-offline';
            var statusText = cam.enabled ? 'Online' : 'Offline';
            card.innerHTML =
                '<div class="camera-preview">No signal — ' + (cam.type || 'unknown') + '</div>' +
                '<div class="camera-info">' +
                    '<h3>' + escapeHtml(cam.name) + '</h3>' +
                    '<div class="meta">' + escapeHtml(cam.resolution || '') + ' @ ' + (cam.framerate || '?') + 'fps</div>' +
                    '<span class="status ' + statusClass + '">' + statusText + '</span>' +
                '</div>';
            container.appendChild(card);
        });
        if (cameras.length === 0) {
            container.innerHTML = '<div class="camera-card"><div class="camera-preview">No cameras configured</div></div>';
        }
    }

    function escapeHtml(str) {
        var div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    loginLink.addEventListener('click', function(e) {
        e.preventDefault();
        loginOverlay.style.display = 'flex';
    });

    loginOverlay.addEventListener('click', function(e) {
        if (e.target === loginOverlay) {
            loginOverlay.style.display = 'none';
        }
    });

    loginBtn.addEventListener('click', function() {
        loginError.style.display = 'none';
        loginError.textContent = 'Login functionality requires proper client-side signature computation.';
        loginError.style.display = 'block';
    });

    settingsLink.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '/settings/main';
    });

    loadCameras();
});
