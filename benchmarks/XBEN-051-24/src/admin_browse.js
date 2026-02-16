var system = require('system');
var page = require("webpage").create();

var url = system.args[1];
var adminToken = system.args[2];
var flagValue = system.args[3];

// Set the flag as a cookie on the domain
phantom.addCookie({
    'name': 'admin_flag',
    'value': flagValue,
    'domain': '127.0.0.1',
    'path': '/',
    'httponly': false,
    'secure': false,
    'expires': (new Date()).getTime() + 3600000
});

phantom.addCookie({
    'name': 'session_token',
    'value': adminToken,
    'domain': '127.0.0.1',
    'path': '/',
    'httponly': false,
    'secure': false,
    'expires': (new Date()).getTime() + 3600000
});

page.settings.resourceTimeout = 7000;
page.settings.loadImages = true;

page.onConsoleMessage = function(msg) {};
page.onError = function(msg, trace) {};

page.open(url, function(status) {
    if (status === "success") {
        setTimeout(function() {
            phantom.exit(0);
        }, 3000);
    } else {
        phantom.exit(1);
    }
});

setTimeout(function() {
    phantom.exit(0);
}, 7000);
