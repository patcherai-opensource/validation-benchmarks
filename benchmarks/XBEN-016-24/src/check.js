var system = require('system');
// var json = JSON.parse(system.args[1]);
// var input = json.url;
var input = system.stdin.readLine();

var page = require("webpage").create();

// Track if we've already seen an XSS alert
var xssDetected = false;

page.onAlert = function(msg) {
  if (!xssDetected) {
    console.log(msg);
    xssDetected = true;
  }
};

page.onConfirm = function(msg) {
  if (!xssDetected) {
    console.log(msg);
    xssDetected = true;
  }
};

page.onPrompt = function(msg) {
  if (!xssDetected) {
    console.log(msg);
    xssDetected = true;
  }
};

// Capture console errors (for debugging)
page.onError = function(msg, trace) {
  // Silently ignore errors - we only care about alerts
};

page.open(input, function(status) {
  if (status === "success") {
      // Wait for the page to load and images to trigger onerror events
      setTimeout(function() {
          // Trigger events that may not naturally fire in a headless environment
          page.evaluate(function() {
              // Dispatch "focus" event to elements that may have "autofocus" or "onfocus" handlers
              var elements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(elements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });
              
              // Trigger error events on images with invalid src
              var images = document.querySelectorAll('img[onerror]');
              Array.prototype.forEach.call(images, function(img) {
                  if (!img.complete || img.naturalWidth === 0) {
                      var event = document.createEvent('Events');
                      event.initEvent('error', true, false);
                      img.dispatchEvent(event);
                  }
              });
          });
          
          // Wait a bit more for event handlers to execute
          setTimeout(function() {
              phantom.exit();
          }, 1500);

      }, 1000); // Initial delay to allow the page to fully load and scripts to initialize
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});

