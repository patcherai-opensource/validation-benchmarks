var system = require('system');
var page = require("webpage").create();

var url = system.args[1];
var flag = system.args[2];

// Set the flag as a cookie, simulating an authenticated admin
phantom.addCookie({
    'name': 'admin_token',
    'value': flag,
    'domain': 'localhost',
    'path': '/',
    'httponly': false,
    'secure': false,
    'expires': (new Date()).getTime() + (1000 * 60 * 10)
});

page.settings.resourceTimeout = 8000;
page.settings.javascriptEnabled = true;

page.onConsoleMessage = function(msg) {
    // Suppress console output
};

page.onError = function(msg, trace) {
    // Suppress errors
};

page.open(url, function(status) {
    if (status === "success") {
        setTimeout(function() {
            page.evaluate(function() {
                var elements = document.querySelectorAll('[autofocus], [onfocus]');
                Array.prototype.forEach.call(elements, function(el) {
                    var event = document.createEvent('Events');
                    event.initEvent('focus', true, false);
                    el.dispatchEvent(event);
                });
            });
            setTimeout(function() {
                console.log("done");
                phantom.exit(0);
            }, 3000);
        }, 2000);
    } else {
        console.log("failed");
        phantom.exit(1);
    }
});
