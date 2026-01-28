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
              // Dispatch animation events to elements that have animation event handlers
              // This is key for CVE-2023-30838 style vulnerabilities
              var animationHandlers = ['onanimationstart', 'onanimationend', 'onanimationiteration', 'onanimationcancel'];
              
              animationHandlers.forEach(function(handler) {
                  var elements = document.querySelectorAll('[' + handler + ']');
                  Array.prototype.forEach.call(elements, function(el) {
                      // Trigger the animation start event
                      var event = document.createEvent('AnimationEvent');
                      if (event.initAnimationEvent) {
                          event.initAnimationEvent('animationstart', true, true, 'testAnimation', 0);
                      } else {
                          event = new AnimationEvent('animationstart', {
                              animationName: 'testAnimation',
                              elapsedTime: 0,
                              bubbles: true,
                              cancelable: true
                          });
                      }
                      el.dispatchEvent(event);
                      
                      // Also trigger via direct attribute call if present
                      if (el.onanimationstart) {
                          el.onanimationstart(event);
                      }
                  });
              });
              
              // Also check for style-based animations that trigger automatically
              var allElements = document.querySelectorAll('*');
              Array.prototype.forEach.call(allElements, function(el) {
                  var style = window.getComputedStyle(el);
                  if (style.animationName && style.animationName !== 'none') {
                      // This element has animation, trigger animation events
                      var event = document.createEvent('Events');
                      event.initEvent('animationstart', true, false);
                      el.dispatchEvent(event);
                  }
              });
              
              // Legacy: Also dispatch "focus" event to elements that may have "autofocus" or "onfocus" handlers
              var focusElements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(focusElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });
          });
          
          // Wait a bit before terminating PhantomJS to allow event handlers to execute
          setTimeout(function() {
              phantom.exit();
          }, 1500);

      }, 1000);
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});
