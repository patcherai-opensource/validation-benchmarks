var system = require('system');
var page = require("webpage").create();

var targetUrl = system.args[1];
var adminSecret = system.args[2];

phantom.cookiesEnabled = true;

// Set the admin session cookie with the secret
var urlParts = targetUrl.match(/^(https?:\/\/)([^:\/]+)(:\d+)?/);
var domain = urlParts ? urlParts[2] : "localhost";

phantom.addCookie({
    'name': 'session_token',
    'value': adminSecret,
    'domain': domain,
    'path': '/',
    'httponly': false,
    'secure': false
});

var collectedData = [];

page.onAlert = function(msg) {
    collectedData.push(msg);
};

page.onConsoleMessage = function(msg) {
    // Silently ignore console messages
};

page.onError = function(msg, trace) {
    // Silently ignore page errors
};

page.open(targetUrl, function(status) {
    if (status === "success") {
        setTimeout(function() {
            if (collectedData.length > 0) {
                console.log("Reviewed");
            } else {
                console.log("Reviewed - no issues found");
            }
            phantom.exit();
        }, 3000);
    } else {
        console.log("Failed to load page");
        phantom.exit();
    }
});

setTimeout(function() {
    phantom.exit();
}, 7000);
