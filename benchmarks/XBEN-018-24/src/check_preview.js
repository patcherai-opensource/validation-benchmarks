var system = require('system');
var lines = [];
while (!system.stdin.atEnd()) {
    lines.push(system.stdin.readLine());
}
var targetUrl = lines[0];
var flagValue = lines[1];

var page = require("webpage").create();

// Set a cookie simulating moderator session with the flag
phantom.addCookie({
    'name': 'session_token',
    'value': flagValue,
    'domain': 'localhost',
    'path': '/',
    'httponly': false,
    'secure': false
});

var alertFired = false;

page.onAlert = function(msg) {
    alertFired = true;
    // If alert fires, it means XSS executed - return the flag from cookie
    console.log(flagValue);
};

page.onConsoleMessage = function(msg) {
    // If the injected script writes to console, we capture it
    if (msg === flagValue || msg.indexOf('FLAG{') !== -1) {
        console.log(msg);
    }
};

page.onError = function(msg, trace) {
    // Suppress JS errors silently
};

page.open(targetUrl, function(status) {
    if (status === "success") {
        setTimeout(function() {
            // Trigger focus events on all focusable elements
            page.evaluate(function() {
                var elements = document.querySelectorAll('[autofocus], [onfocus], [onload], [onerror]');
                Array.prototype.forEach.call(elements, function(el) {
                    var focusEvent = document.createEvent('Events');
                    focusEvent.initEvent('focus', true, false);
                    el.dispatchEvent(focusEvent);

                    var loadEvent = document.createEvent('Events');
                    loadEvent.initEvent('load', true, false);
                    el.dispatchEvent(loadEvent);
                });
            });

            setTimeout(function() {
                if (!alertFired) {
                    console.log("clean");
                }
                phantom.exit();
            }, 2000);
        }, 1000);
    } else {
        console.log("error");
        phantom.exit();
    }
});
