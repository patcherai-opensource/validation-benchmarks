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
              // Dispatch "focus" and "focusin" events to elements that may have relevant handlers
              var elements = document.querySelectorAll('[autofocus], [onfocus], [onfocusin], [tabindex]');
              Array.prototype.forEach.call(elements, function(el) {
                  // Trigger focus event
                  var focusEvent = document.createEvent('Events');
                  focusEvent.initEvent('focus', true, false);
                  el.dispatchEvent(focusEvent);
                  
                  // Also trigger focusin event (bubbles unlike focus)
                  var focusinEvent = document.createEvent('Events');
                  focusinEvent.initEvent('focusin', true, false);
                  el.dispatchEvent(focusinEvent);
              });
              
              // Also trigger animationstart/end events on elements with those handlers
              var animElements = document.querySelectorAll('[onanimationstart], [onanimationend], [onanimationiteration]');
              Array.prototype.forEach.call(animElements, function(el) {
                  var animStartEvent = document.createEvent('Events');
                  animStartEvent.initEvent('animationstart', true, false);
                  el.dispatchEvent(animStartEvent);
                  
                  var animEndEvent = document.createEvent('Events');
                  animEndEvent.initEvent('animationend', true, false);
                  el.dispatchEvent(animEndEvent);
              });
              
              // Trigger transition events
              var transElements = document.querySelectorAll('[ontransitionend], [ontransitionstart]');
              Array.prototype.forEach.call(transElements, function(el) {
                  var transEvent = document.createEvent('Events');
                  transEvent.initEvent('transitionend', true, false);
                  el.dispatchEvent(transEvent);
              });
              
              // Trigger pointer events
              var pointerElements = document.querySelectorAll('[onpointerdown], [onpointerup], [onpointermove], [onpointerenter], [onpointerleave]');
              Array.prototype.forEach.call(pointerElements, function(el) {
                  var pointerEvent = document.createEvent('Events');
                  pointerEvent.initEvent('pointerenter', true, false);
                  el.dispatchEvent(pointerEvent);
              });
          });
          
          // Optionally, add more events here like "mouseover" if needed
          // Ensure to wait a bit before terminating PhantomJS to allow event handlers to execute
          setTimeout(function() {
              phantom.exit();
          }, 1000); // Adjust timeout as necessary based on observed behavior

      }, 1000); // Initial delay to allow the page to fully load and scripts to initialize
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});
