var system = require('system');
var webpage = require('webpage');

var configStr = system.stdin.readLine();
var config = JSON.parse(configStr);

var baseUrl = config.base_url;
var adminSecret = config.admin_secret;

var page = webpage.create();
page.settings.resourceTimeout = 10000;
page.customHeaders = {'Content-Type': 'application/x-www-form-urlencoded'};

page.onError = function(msg, trace) {};

// Set the flag cookie on the domain before any page loads
phantom.addCookie({
    'name': 'admin_secret',
    'value': adminSecret,
    'domain': '127.0.0.1',
    'path': '/',
    'httponly': false,
    'secure': false,
    'expires': (new Date()).getTime() + (1000 * 60 * 60 * 24)
});

// Step 1: POST login credentials directly
page.open(baseUrl + '/admin/login', 'POST', 'faqusername=admin&faqpassword=admin_phpmyfaq_2024!', function(status) {
    if (status !== 'success') {
        phantom.exit(1);
        return;
    }

    // Clear the custom content-type for subsequent GET requests
    page.customHeaders = {};

    // After login redirect, we should be authenticated
    // Now visit user management page
    setTimeout(function() {
        page.open(baseUrl + '/admin/user', function(status2) {
            if (status2 !== 'success') {
                phantom.exit(1);
                return;
            }

            // Wait for AJAX user list to load and any XSS to fire from list view
            setTimeout(function() {
                // Click view for each user to also trigger detail view XSS
                page.evaluate(function() {
                    var links = document.querySelectorAll('a[onclick*="viewUser"]');
                    for (var i = 0; i < links.length; i++) {
                        try { links[i].click(); } catch(e) {}
                    }
                });

                // Wait for detail XSS payloads to execute and any exfiltration to complete
                setTimeout(function() {
                    phantom.exit(0);
                }, 5000);
            }, 4000);
        });
    }, 1000);
});
