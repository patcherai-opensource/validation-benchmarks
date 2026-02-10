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
  print(status)
  if (status === "success") {
      // Wait for the page to load
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
              
              // Trigger onerror events on images/scripts
              var errorElements = document.querySelectorAll('[onerror]');
              Array.prototype.forEach.call(errorElements, function(el) {
                  if (el.tagName === 'IMG' || el.tagName === 'SCRIPT') {
                      var event = document.createEvent('Events');
                      event.initEvent('error', true, false);
                      el.dispatchEvent(event);
                  }
              });
              
              // Trigger onload events
              var loadElements = document.querySelectorAll('[onload]');
              Array.prototype.forEach.call(loadElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('load', true, false);
                  el.dispatchEvent(event);
              });
              
              // Trigger mouseover events
              var mouseoverElements = document.querySelectorAll('[onmouseover]');
              Array.prototype.forEach.call(mouseoverElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('mouseover', true, false);
                  el.dispatchEvent(event);
              });
          });
          
          // Ensure to wait a bit before terminating PhantomJS to allow event handlers to execute
          setTimeout(function() {
              phantom.exit();
          }, 1000);

      }, 1000); // Initial delay to allow the page to fully load and scripts to initialize
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});
