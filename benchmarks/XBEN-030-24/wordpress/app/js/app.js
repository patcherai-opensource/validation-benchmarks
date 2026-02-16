function showTab(tabId) {
    var tabs = document.querySelectorAll('.tab-content');
    var btns = document.querySelectorAll('.tab-btn');
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
    }
    for (var i = 0; i < btns.length; i++) {
        btns[i].classList.remove('active');
    }
    document.getElementById('tab-' + tabId).classList.add('active');
    event.target.classList.add('active');
}

function generateKey(entityName) {
    var csrfToken = document.querySelector('meta[name=csrf_token]').getAttribute('content');
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'ajax/networking/gen_tunnelkey.php', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            try {
                var data = JSON.parse(xhr.responseText);
                if (data.pubkey) {
                    var targetId = entityName === 'wg-server' ? 'server-pubkey' : 'peer-pubkey';
                    document.getElementById(targetId).value = data.pubkey;
                }
            } catch (e) {
                console.log('Key generation completed');
            }
        }
    };
    xhr.send('node=' + encodeURIComponent(entityName) + '&csrf_token=' + encodeURIComponent(csrfToken));
}

function loadInterfaceSummary(iface) {
    var csrfToken = document.querySelector('meta[name=csrf_token]').getAttribute('content');
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'ajax/networking/get_ip_summary.php', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            try {
                var data = JSON.parse(xhr.responseText);
                var target = document.getElementById('interface-summary');
                if (target && data.output) {
                    target.innerHTML = '<pre>' + data.output.join('\n') + '</pre>';
                }
            } catch (e) {}
        }
    };
    xhr.send('interface=' + encodeURIComponent(iface) + '&csrf_token=' + encodeURIComponent(csrfToken));
}

document.addEventListener('DOMContentLoaded', function() {
    var summary = document.getElementById('interface-summary');
    if (summary) {
        loadInterfaceSummary('eth0');
    }
});
