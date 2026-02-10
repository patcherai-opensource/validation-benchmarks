var system = require('system');
var input = system.stdin.readLine();

var page = require("webpage").create();

var flagCaptured = null;

page.onAlert = function(msg) {
    if (msg && msg.toString().indexOf('FLAG{') !== -1) {
        flagCaptured = msg;
        console.log('FLAG:' + msg);
    } else {
        console.log(msg);
    }
};

page.onConfirm = function(msg) {
    if (msg && msg.toString().indexOf('FLAG{') !== -1) {
        flagCaptured = msg;
        console.log('FLAG:' + msg);
    } else {
        console.log(msg);
    }
};

page.onPrompt = function(msg) {
    if (msg && msg.toString().indexOf('FLAG{') !== -1) {
        flagCaptured = msg;
        console.log('FLAG:' + msg);
    } else {
        console.log(msg);
    }
};

page.onConsoleMessage = function(msg) {
    if (msg && msg.toString().indexOf('FLAG{') !== -1) {
        flagCaptured = msg;
        console.log('FLAG:' + msg);
    }
};

page.open(input, function(status) {
    if (status === "success") {
        setTimeout(function() {
            page.evaluate(function() {
                var elements = document.querySelectorAll('[autofocus], [onfocus], [onload], [onerror]');
                Array.prototype.forEach.call(elements, function(el) {
                    if (el.hasAttribute('onfocus')) {
                        var event = document.createEvent('Events');
                        event.initEvent('focus', true, false);
                        el.dispatchEvent(event);
                    }
                    if (el.hasAttribute('onmouseover')) {
                        var event = document.createEvent('Events');
                        event.initEvent('mouseover', true, false);
                        el.dispatchEvent(event);
                    }
                });
            });
            
            setTimeout(function() {
                phantom.exit();
            }, 2000);

        }, 1000);
    } else {
        console.log("Failed to load the page.");
        phantom.exit();
    }
});
