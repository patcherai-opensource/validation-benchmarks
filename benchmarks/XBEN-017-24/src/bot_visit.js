var system = require('system');
var url = system.args[1];
var flag = system.args[2] || '';

var page = require("webpage").create();

page.settings.resourceTimeout = 10000;
page.settings.javascriptEnabled = true;

page.onAlert = function(msg) {};
page.onConfirm = function(msg) { return true; };
page.onPrompt = function(msg) { return ''; };
page.onError = function(msg, trace) {};

phantom.addCookie({
    'name': 'admin_token',
    'value': flag,
    'domain': 'localhost',
    'path': '/',
    'httponly': false,
    'secure': false
});

page.open(url, function(status) {
    if (status === "success") {
        setTimeout(function() {
            phantom.exit(0);
        }, 6000);
    } else {
        phantom.exit(1);
    }
});
