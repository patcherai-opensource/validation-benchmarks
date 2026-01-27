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
              // Helper function to trigger inline event handlers
              function triggerInlineHandler(element, attrName) {
                  var handler = element.getAttribute(attrName);
                  if (handler) {
                      try {
                          // Create a function from the handler and call it
                          var fn = new Function('event', handler);
                          fn.call(element, { target: element, type: attrName.replace('on', '') });
                      } catch(e) {
                          console.log('Error executing handler: ' + e);
                      }
                  }
              }
              
              // Dispatch "focus" event to elements that may have "autofocus" or "onfocus" handlers
              var elements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(elements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
                  triggerInlineHandler(el, 'onfocus');
              });
              
              // List of pointer event attributes to check for
              var pointerEventAttrs = [
                  'onpointerdown', 'onpointerup', 'onpointerover', 'onpointermove',
                  'onpointerout', 'onpointerenter', 'onpointerleave', 'onpointercancel',
                  'ongotpointercapture', 'onlostpointercapture'
              ];
              
              // Find all elements with pointer event handlers and trigger them
              pointerEventAttrs.forEach(function(attr) {
                  var elements = document.querySelectorAll('[' + attr + ']');
                  Array.prototype.forEach.call(elements, function(el) {
                      // Try to dispatch the event first
                      try {
                          var eventName = attr.replace('on', '');
                          var event = document.createEvent('Events');
                          event.initEvent(eventName, true, true);
                          el.dispatchEvent(event);
                      } catch(e) {
                          // Event dispatch failed, try direct handler invocation
                      }
                      
                      // Also directly invoke the inline handler
                      triggerInlineHandler(el, attr);
                  });
              });
              
              // Also trigger mouse events as fallback for pointer events
              var mouseEventAttrs = ['onmousedown', 'onmouseup', 'onmouseover', 'onmouseout', 'onmouseenter', 'onmouseleave'];
              mouseEventAttrs.forEach(function(attr) {
                  var elements = document.querySelectorAll('[' + attr + ']');
                  Array.prototype.forEach.call(elements, function(el) {
                      var eventName = attr.replace('on', '');
                      var event = document.createEvent('MouseEvents');
                      event.initMouseEvent(eventName, true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
                      el.dispatchEvent(event);
                  });
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
