var system = require('system');
var input = system.stdin.readLine();

var page = require("webpage").create();

page.settings.javascriptEnabled = true;
page.settings.loadImages = true;
page.settings.webSecurityEnabled = false;

page.onAlert = function(msg) {
    console.log(msg);
};

page.onConfirm = function(msg) {
    console.log(msg);
};

page.onPrompt = function(msg) {
    console.log(msg);
};

page.onError = function(msg, trace) {
    // Suppress JS errors silently
};

page.open(input, function(status) {
    if (status === "success") {
        setTimeout(function() {
            page.evaluate(function() {
                // Trigger focus events on elements with onfocus handlers
                var focusable = document.querySelectorAll('[autofocus], [onfocus]');
                Array.prototype.forEach.call(focusable, function(el) {
                    var evt = document.createEvent('Events');
                    evt.initEvent('focus', true, false);
                    el.dispatchEvent(evt);
                });
                // Trigger mouseover events
                var hoverable = document.querySelectorAll('[onmouseover]');
                Array.prototype.forEach.call(hoverable, function(el) {
                    var evt = document.createEvent('Events');
                    evt.initEvent('mouseover', true, false);
                    el.dispatchEvent(evt);
                });
            });

            setTimeout(function() {
                phantom.exit();
            }, 2000);
        }, 1500);
    } else {
        phantom.exit();
    }
});

