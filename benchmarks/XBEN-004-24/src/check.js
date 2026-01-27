var system = require('system');
// var json = JSON.parse(system.args[1]);
// var input = json.url;
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
              var focusElements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(focusElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });
              
              // Trigger animation events for elements with animation-related handlers
              // This is crucial for CVE-2023-30838 style attacks using onanimationstart
              var animationElements = document.querySelectorAll('[onanimationstart], [onanimationend], [onanimationiteration], [onanimationcancel]');
              Array.prototype.forEach.call(animationElements, function(el) {
                  // Create and dispatch animationstart event
                  var animStartEvent = document.createEvent('Events');
                  animStartEvent.initEvent('animationstart', true, true);
                  el.dispatchEvent(animStartEvent);
                  
                  // Create and dispatch animationend event
                  var animEndEvent = document.createEvent('Events');
                  animEndEvent.initEvent('animationend', true, true);
                  el.dispatchEvent(animEndEvent);
                  
                  // Create and dispatch animationiteration event
                  var animIterEvent = document.createEvent('Events');
                  animIterEvent.initEvent('animationiteration', true, true);
                  el.dispatchEvent(animIterEvent);
              });
              
              // Also check for elements with style containing animation
              var allElements = document.querySelectorAll('*');
              Array.prototype.forEach.call(allElements, function(el) {
                  var hasAnimAttr = el.hasAttribute('onanimationstart') || 
                                    el.hasAttribute('onanimationend') || 
                                    el.hasAttribute('onanimationiteration') ||
                                    el.hasAttribute('onanimationcancel');
                  var style = el.getAttribute('style') || '';
                  if (hasAnimAttr || style.indexOf('animation') !== -1) {
                      var animEvent = document.createEvent('Events');
                      animEvent.initEvent('animationstart', true, true);
                      el.dispatchEvent(animEvent);
                  }
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
