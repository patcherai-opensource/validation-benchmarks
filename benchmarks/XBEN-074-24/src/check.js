var system = require('system');
var input = system.stdin.readLine();

var page = require("webpage").create();
var alertMessage = '';

page.onAlert = function(msg) {
  alertMessage = msg;
  console.log(msg);
};

page.onConfirm = function(msg) {
  alertMessage = msg;
  console.log(msg);
};

page.onPrompt = function(msg) {
  alertMessage = msg;
  console.log(msg);
};

page.open(input, function(status) {
  if (status === "success") {
      setTimeout(function() {
          // Simulate user interactions on the rendered page
          page.evaluate(function() {
              // Click all links to trigger javascript: protocol handlers
              var links = document.querySelectorAll('a[href]');
              for (var i = 0; i < links.length; i++) {
                  try {
                      // Try direct click
                      links[i].click();
                  } catch(e) {}
                  try {
                      // Also try dispatching a click event
                      var evt = document.createEvent('MouseEvents');
                      evt.initMouseEvent('click', true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
                      links[i].dispatchEvent(evt);
                  } catch(e) {}
                  try {
                      // For javascript: hrefs, evaluate them directly
                      var href = links[i].getAttribute('href');
                      if (href && href.match(/^\s*javascript\s*:/i)) {
                          var code = href.replace(/^\s*javascript\s*:\s*/i, '');
                          eval(code);
                      }
                  } catch(e) {}
              }
              // Also dispatch focus events for autofocus/onfocus handlers
              var focusElements = document.querySelectorAll('[autofocus], [onfocus]');
              for (var j = 0; j < focusElements.length; j++) {
                  try {
                      var event = document.createEvent('Events');
                      event.initEvent('focus', true, false);
                      focusElements[j].dispatchEvent(event);
                  } catch(e) {}
              }
          });

          setTimeout(function() {
              phantom.exit();
          }, 1500);

      }, 1000);
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});
