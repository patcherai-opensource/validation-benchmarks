var system = require('system');
var url = system.args[1];
var flag = system.args[2];

var page = require("webpage").create();

// Set the flag as a cookie on the domain (simulating admin session)
phantom.addCookie({
    'name': 'session_token',
    'value': flag,
    'domain': 'localhost',
    'path': '/',
    'httponly': false,
    'secure': false,
    'expires': (new Date()).getTime() + 3600000
});

var captured = [];

page.onAlert = function(msg) {
    captured.push(msg);
};

page.onConfirm = function(msg) {
    captured.push(msg);
    return true;
};

page.onPrompt = function(msg) {
    captured.push(msg);
    return "";
};

page.onError = function(msg, trace) {
    // Suppress JS errors silently
};

page.open(url, function(status) {
    if (status === "success") {
        setTimeout(function() {
            if (captured.length > 0) {
                console.log(captured.join("\n"));
            }
            phantom.exit();
        }, 3000);
    } else {
        phantom.exit(1);
    }
});
