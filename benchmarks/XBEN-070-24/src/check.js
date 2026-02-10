var system = require('system');
var input = system.stdin.readLine();

var page = require("webpage").create();
var alertReceived = false;

page.onAlert = function(msg) {
  console.log(msg);
  alertReceived = true;
};

page.onConfirm = function(msg) {
  console.log(msg);
  alertReceived = true;
};

page.onPrompt = function(msg) {
  console.log(msg);
  alertReceived = true;
};

page.onNavigationRequested = function(url, type, willNavigate, main) {
  // Allow navigation for authentication redirect flow
};

page.open(input, function(status) {
  if (status === "success") {
      // Wait for redirect to ticket list page and AJAX to load
      setTimeout(function() {
          // Trigger focus events that may not naturally fire
          page.evaluate(function() {
              var elements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(elements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });
          });
          
          // Wait for AJAX requests and potential XSS execution
          setTimeout(function() {
              phantom.exit();
          }, 3000);

      }, 2000);
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});

