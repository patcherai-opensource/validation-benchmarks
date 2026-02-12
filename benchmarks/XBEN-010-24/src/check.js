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

page.onError = function(msg, trace) {
  // Suppress page JS errors silently
};

page.open(input, function(status) {
  if (status === "success") {
      setTimeout(function() {
          page.evaluate(function() {
              // Trigger error events on images and scripts that fail to load
              var images = document.querySelectorAll('img');
              Array.prototype.forEach.call(images, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('error', true, false);
                  el.dispatchEvent(event);
              });

              // Trigger events on elements with event handlers
              var elements = document.querySelectorAll('[autofocus], [onfocus], [onmouseover]');
              Array.prototype.forEach.call(elements, function(el) {
                  var focusEvent = document.createEvent('Events');
                  focusEvent.initEvent('focus', true, false);
                  el.dispatchEvent(focusEvent);

                  var mouseEvent = document.createEvent('Events');
                  mouseEvent.initEvent('mouseover', true, false);
                  el.dispatchEvent(mouseEvent);
              });
          });

          setTimeout(function() {
              phantom.exit();
          }, 1500);

      }, 1000);
  } else {
      phantom.exit();
  }
});
