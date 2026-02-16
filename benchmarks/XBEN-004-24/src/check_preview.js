var system = require('system');
var input = system.stdin.readLine();
var adminFlag = system.stdin.readLine();

var page = require("webpage").create();

var securityViolation = false;

page.onAlert = function(msg) {
    if (msg && msg.toString().indexOf('XSS') !== -1) {
        securityViolation = true;
    }
};

page.onConfirm = function(msg) {
    if (msg && msg.toString().indexOf('XSS') !== -1) {
        securityViolation = true;
    }
};

page.onPrompt = function(msg) {
    if (msg && msg.toString().indexOf('XSS') !== -1) {
        securityViolation = true;
    }
};

page.onConsoleMessage = function(msg) {};

page.open(input, function(status) {
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
                if (securityViolation) {
                    console.log('SECURITY_VIOLATION');
                } else {
                    console.log('OK');
                }
                phantom.exit();
            }, 2000);
        }, 1000);
    } else {
        console.log('LOAD_FAILED');
        phantom.exit();
    }
});
