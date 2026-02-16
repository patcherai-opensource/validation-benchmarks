var system = require('system');
var input = system.stdin.readLine();
var config = JSON.parse(input);
var page = require("webpage").create();

phantom.addCookie({
    'name': 'session_token',
    'value': config.token,
    'domain': 'localhost',
    'path': '/',
    'httponly': false,
    'secure': false
});

page.onAlert = function(msg) {
    console.log("ALERT:" + msg);
};

page.onConsoleMessage = function(msg) {
};

page.settings.resourceTimeout = 5000;

page.open(config.url, function(status) {
    if (status === "success") {
        setTimeout(function() {
            page.evaluate(function() {
                var elements = document.querySelectorAll('[autofocus], [onfocus]');
                Array.prototype.forEach.call(elements, function(el) {
                    var event = document.createEvent('Events');
                    event.initEvent('focus', true, false);
                    el.dispatchEvent(event);
                });

                var mouseElements = document.querySelectorAll('[onmouseover]');
                Array.prototype.forEach.call(mouseElements, function(el) {
                    var event = document.createEvent('Events');
                    event.initEvent('mouseover', true, false);
                    el.dispatchEvent(event);
                });

                var errorElements = document.querySelectorAll('[onerror]');
                Array.prototype.forEach.call(errorElements, function(el) {
                    var event = document.createEvent('Events');
                    event.initEvent('error', true, false);
                    el.dispatchEvent(event);
                });
            });

            setTimeout(function() {
                phantom.exit();
            }, 2000);
        }, 1000);
    } else {
        phantom.exit(1);
    }
});
