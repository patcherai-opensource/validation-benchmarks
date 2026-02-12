var system = require('system');
var input = system.stdin.readLine();
var data = JSON.parse(input);
var url = data.url;
var token = data.token;

var page = require("webpage").create();

// Set the admin session cookie before visiting
phantom.addCookie({
    'name': 'admin_token',
    'value': token,
    'domain': 'localhost',
    'path': '/',
    'httponly': false,
    'secure': false
});

page.settings.resourceTimeout = 8000;

page.open(url, function(status) {
    if (status === "success") {
        // Wait for page to load and any scripts to execute
        setTimeout(function() {
            phantom.exit(0);
        }, 5000);
    } else {
        phantom.exit(1);
    }
});

// Timeout safety
setTimeout(function() {
    phantom.exit(0);
}, 9000);
