var system = require('system');
var webpage = require('webpage');

// Arguments: base_url, flag_value, url_to_visit
var base_url = system.args[1];
var flag_value = system.args[2];
var target_url = system.args[3];

var page = webpage.create();

// Set the flag as a cookie on the server domain
phantom.addCookie({
    'name': 'session_token',
    'value': flag_value,
    'domain': 'localhost',
    'path': '/',
    'httponly': false,
    'secure': false,
    'expires': (new Date()).getTime() + (1000 * 60 * 60)
});

page.settings.resourceTimeout = 5000;

page.onAlert = function(msg) {
    console.log("alert: " + msg);
};

page.onConsoleMessage = function(msg) {
    // Suppress console output
};

page.onError = function(msg, trace) {
    // Suppress JS errors
};

page.open(target_url, function(status) {
    if (status === "success") {
        // Wait for the page to fully load and scripts to execute
        setTimeout(function() {
            phantom.exit(0);
        }, 3000);
    } else {
        console.log("Failed to load: " + target_url);
        phantom.exit(1);
    }
});
