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
      setTimeout(function() {
          page.evaluate(function() {
              // Simulate user interactions that might trigger event handlers
              // This simulates how a real user might interact with the page
              
              // Trigger focus events on elements that may have focus-related handlers
              var focusableElements = document.querySelectorAll('[autofocus], [onfocus], [tabindex], input, textarea, button, a, select');
              Array.prototype.forEach.call(focusableElements, function(el) {
                  try {
                      var focusEvent = document.createEvent('Events');
                      focusEvent.initEvent('focus', true, false);
                      el.dispatchEvent(focusEvent);
                      
                      var focusinEvent = document.createEvent('Events');
                      focusinEvent.initEvent('focusin', true, false);
                      el.dispatchEvent(focusinEvent);
                  } catch(e) {}
              });
              
              // Trigger mouse events on interactive elements
              var interactiveElements = document.querySelectorAll('*');
              Array.prototype.forEach.call(interactiveElements, function(el) {
                  try {
                      // Check if element has any on* attribute
                      var attrs = el.attributes;
                      for (var i = 0; i < attrs.length; i++) {
                          if (attrs[i].name.toLowerCase().indexOf('on') === 0) {
                              // Try to trigger various events
                              var events = ['mouseenter', 'mouseover', 'mousedown', 'mouseup', 'focus', 'focusin', 'auxclick', 'toggle'];
                              events.forEach(function(eventName) {
                                  try {
                                      var evt = document.createEvent('Events');
                                      evt.initEvent(eventName, true, false);
                                      el.dispatchEvent(evt);
                                  } catch(e) {}
                              });
                              break;
                          }
                      }
                  } catch(e) {}
              });
              
              // Handle details/summary elements for ontoggle
              var detailsElements = document.querySelectorAll('details');
              Array.prototype.forEach.call(detailsElements, function(el) {
                  try {
                      el.open = !el.open;
                      var toggleEvent = document.createEvent('Events');
                      toggleEvent.initEvent('toggle', true, false);
                      el.dispatchEvent(toggleEvent);
                  } catch(e) {}
              });
          });
          
          setTimeout(function() {
              phantom.exit();
          }, 1000);

      }, 1000);
  } else {
      phantom.exit();
  }
});

