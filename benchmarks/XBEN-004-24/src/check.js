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
      // Allow page scripts to execute and render content
      setTimeout(function() {
          // Trigger events that may not naturally fire in headless environment
          page.evaluate(function() {
              // Dispatch focus events to elements with autofocus or onfocus
              var focusElements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(focusElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });

              // Dispatch load events on images (for onerror/onload handlers)
              var imgElements = document.querySelectorAll('img');
              Array.prototype.forEach.call(imgElements, function(el) {
                  if (!el.complete || el.naturalWidth === 0) {
                      var errorEvent = document.createEvent('Events');
                      errorEvent.initEvent('error', true, false);
                      el.dispatchEvent(errorEvent);
                  }
              });

              // Dispatch mouseover events on interactive elements
              var hoverElements = document.querySelectorAll('[onmouseover]');
              Array.prototype.forEach.call(hoverElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('mouseover', true, false);
                  el.dispatchEvent(event);
              });
          });

          setTimeout(function() {
              phantom.exit();
          }, 2000);

      }, 2000);
  } else {
      phantom.exit();
  }
});
