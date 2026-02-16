var system = require('system');
var input = system.stdin.readLine();
var page = require("webpage").create();

var capturedData = [];

// Capture alert() calls from the page
page.onAlert = function(msg) {
    capturedData.push(msg);
};

// Capture console.log() calls from the page
page.onConsoleMessage = function(msg) {
    capturedData.push(msg);
};

// Capture window.callPhantom() calls
page.onCallback = function(data) {
    if (data) {
        capturedData.push(typeof data === 'string' ? data : JSON.stringify(data));
    }
};

page.open(input, function(status) {
    if (status === "success") {
        setTimeout(function() {
            // Trigger focus/load events that might not naturally fire in headless mode
            page.evaluate(function() {
                var elements = document.querySelectorAll('[autofocus], [onfocus], [onload]');
                Array.prototype.forEach.call(elements, function(el) {
                    var event = document.createEvent('Events');
                    event.initEvent('focus', true, false);
                    el.dispatchEvent(event);
                });
                var imgs = document.querySelectorAll('img[onerror]');
                Array.prototype.forEach.call(imgs, function(el) {
                    if (!el.complete || el.naturalWidth === 0) {
                        var event = document.createEvent('Events');
                        event.initEvent('error', true, false);
                        el.dispatchEvent(event);
                    }
                });
            });

            setTimeout(function() {
                // Output all captured data to stdout
                for (var i = 0; i < capturedData.length; i++) {
                    system.stdout.write(capturedData[i] + '\n');
                }
                phantom.exit();
            }, 3000);
        }, 2000);
    } else {
        phantom.exit(1);
    }
});
