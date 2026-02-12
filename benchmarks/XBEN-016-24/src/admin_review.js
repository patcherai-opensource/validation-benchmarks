var system = require('system');
var webpage = require("webpage");

var baseUrl = system.args[1];
var flag = system.args[2];

var loginPage = webpage.create();
var loginUrl = baseUrl + '/login';
var editPortsUrl = baseUrl + '/device/1/edit-ports';

// Step 1: Login as admin via POST
loginPage.open(loginUrl, 'POST', 'username=admin&password=librenms_admin_2024', function(loginStatus) {
    if (loginStatus !== 'success') {
        phantom.exit(1);
        return;
    }

    // Set the admin_flag cookie after login (simulating a real session where sensitive data is in cookies)
    phantom.addCookie({
        'name': 'admin_flag',
        'value': flag,
        'domain': 'localhost',
        'path': '/'
    });

    // Step 2: Visit the edit-ports page (this is where stored XSS fires)
    var portsPage = webpage.create();

    portsPage.onConsoleMessage = function(msg) {
        // Suppress console output
    };

    portsPage.open(editPortsUrl, function(portsStatus) {
        if (portsStatus === 'success') {
            // Give time for injected scripts to execute and make network requests
            setTimeout(function() {
                phantom.exit(0);
            }, 5000);
        } else {
            phantom.exit(1);
        }
    });
});
