var system = require('system');
var input = system.stdin.readLine();

var page = require("webpage").create();

page.onAlert = function(msg) {
  console.log(msg);
};

page.onConfirm = function(msg) {
  console.log(msg);
};

page.onPrompt = function(msg) {
  console.log(msg);
};

page.open(input, function(status) {
  if (status === "success") {
      // Wait for the page to load
      setTimeout(function() {
          // Trigger various events that may not naturally fire in headless environment
          page.evaluate(function() {
              // Dispatch "focus" event to elements that may have "autofocus" or "onfocus" handlers
              var focusElements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(focusElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });
              
              // Dispatch "mouseover" event for onmouseover handlers
              var mouseoverElements = document.querySelectorAll('[onmouseover]');
              Array.prototype.forEach.call(mouseoverElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('mouseover', true, false);
                  el.dispatchEvent(event);
              });
              
              // Dispatch "error" event for onerror handlers (for img tags, etc.)
              var errorElements = document.querySelectorAll('[onerror]');
              Array.prototype.forEach.call(errorElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('error', true, false);
                  el.dispatchEvent(event);
              });
          });
          
          // Ensure to wait a bit before terminating PhantomJS to allow event handlers to execute
          setTimeout(function() {
              phantom.exit();
          }, 1000);

      }, 1000); // Initial delay to allow the page to fully load and scripts to initialize
  } else {
      phantom.exit();
  }
});

