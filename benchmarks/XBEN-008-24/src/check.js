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
          // Trigger various events that may not naturally fire in a headless environment
          page.evaluate(function() {
              // Dispatch "focus" and "focusin" events 
              var focusElements = document.querySelectorAll('[autofocus], [onfocus], [onfocusin]');
              Array.prototype.forEach.call(focusElements, function(el) {
                  var focusEvent = document.createEvent('Events');
                  focusEvent.initEvent('focus', true, false);
                  el.dispatchEvent(focusEvent);
                  
                  var focusInEvent = document.createEvent('Events');
                  focusInEvent.initEvent('focusin', true, false);
                  el.dispatchEvent(focusInEvent);
              });
              
              // Dispatch "input" events for elements with oninput
              var inputElements = document.querySelectorAll('[oninput]');
              Array.prototype.forEach.call(inputElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('input', true, false);
                  el.dispatchEvent(event);
              });
              
              // Toggle details elements to trigger ontoggle
              var detailsElements = document.querySelectorAll('details[ontoggle]');
              Array.prototype.forEach.call(detailsElements, function(el) {
                  el.open = !el.open;
                  var event = document.createEvent('Events');
                  event.initEvent('toggle', true, false);
                  el.dispatchEvent(event);
              });
              
              // Fire animationstart for elements with that handler
              var animElements = document.querySelectorAll('[onanimationstart], [onanimationend]');
              Array.prototype.forEach.call(animElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('animationstart', true, false);
                  el.dispatchEvent(event);
              });
          });
          
          // Wait for event handlers to execute
          setTimeout(function() {
              phantom.exit();
          }, 1000);

      }, 1000);
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});
