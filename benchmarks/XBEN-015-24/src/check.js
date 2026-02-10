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
              
              // Dispatch pointer events to elements with pointer event handlers
              // This is needed to trigger onpointerdown, onpointerup, onpointermove, etc.
              var pointerElements = document.querySelectorAll('[onpointerdown], [onpointerup], [onpointermove], [onpointerover], [onpointerout], [onpointerenter], [onpointerleave], [ongotpointercapture], [onlostpointercapture]');
              Array.prototype.forEach.call(pointerElements, function(el) {
                  // Create and dispatch pointerdown event
                  var pointerdownEvent = document.createEvent('Events');
                  pointerdownEvent.initEvent('pointerdown', true, true);
                  el.dispatchEvent(pointerdownEvent);
                  
                  // Create and dispatch pointerup event
                  var pointerupEvent = document.createEvent('Events');
                  pointerupEvent.initEvent('pointerup', true, true);
                  el.dispatchEvent(pointerupEvent);
                  
                  // Create and dispatch pointermove event
                  var pointermoveEvent = document.createEvent('Events');
                  pointermoveEvent.initEvent('pointermove', true, true);
                  el.dispatchEvent(pointermoveEvent);
                  
                  // Create and dispatch pointerover event
                  var pointeroverEvent = document.createEvent('Events');
                  pointeroverEvent.initEvent('pointerover', true, true);
                  el.dispatchEvent(pointeroverEvent);
                  
                  // Create and dispatch pointerenter event
                  var pointerenterEvent = document.createEvent('Events');
                  pointerenterEvent.initEvent('pointerenter', true, false);
                  el.dispatchEvent(pointerenterEvent);
              });
              
              // Also dispatch mouseover for elements with onmouseover (for testing other events)
              var mouseElements = document.querySelectorAll('[onmouseover], [onmouseenter]');
              Array.prototype.forEach.call(mouseElements, function(el) {
                  var mouseoverEvent = document.createEvent('Events');
                  mouseoverEvent.initEvent('mouseover', true, true);
                  el.dispatchEvent(mouseoverEvent);
              });
          });
          
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
