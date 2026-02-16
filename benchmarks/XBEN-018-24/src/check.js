var system = require('system');
var input = system.stdin.readLine();
var page = require("webpage").create();
var alertMsg = '';

page.onAlert = function(msg) {
    if (!alertMsg) {
        alertMsg = msg;
    }
};

page.onConfirm = function(msg) {
    if (!alertMsg) {
        alertMsg = msg;
    }
};

page.onPrompt = function(msg) {
    if (!alertMsg) {
        alertMsg = msg;
    }
};

page.onError = function(msg, trace) {};

page.onConsoleMessage = function(msg) {};

page.open(input, function(status) {
    if (status === "success") {
        setTimeout(function() {
            try {
                page.evaluate(function() {
                    try {
                        var selectors = '[onfocus], [onerror], [onload], [onmouseover]';
                        var elements = document.querySelectorAll(selectors);
                        for (var i = 0; i < elements.length; i++) {
                            var el = elements[i];
                            var events = ['focus', 'error', 'load', 'mouseover'];
                            for (var j = 0; j < events.length; j++) {
                                try {
                                    var ev = document.createEvent('Events');
                                    ev.initEvent(events[j], true, false);
                                    el.dispatchEvent(ev);
                                } catch(e) {}
                            }
                        }
                        var imgs = document.querySelectorAll('img');
                        for (var k = 0; k < imgs.length; k++) {
                            try {
                                if (!imgs[k].complete || imgs[k].naturalWidth === 0) {
                                    var imgEv = document.createEvent('Events');
                                    imgEv.initEvent('error', true, false);
                                    imgs[k].dispatchEvent(imgEv);
                                }
                            } catch(e) {}
                        }
                    } catch(e) {}
                });
            } catch(e) {}
            setTimeout(function() {
                if (alertMsg) {
                    console.log(alertMsg);
                }
                phantom.exit();
            }, 2000);
        }, 1500);
    } else {
        phantom.exit();
    }
});

