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
      // Wait for the page to load and CSS animations to start
      setTimeout(function() {
          // Trigger events that may not naturally fire in a headless environment
          page.evaluate(function() {
              // Create a style element with a simple animation if not already present
              var styleExists = document.querySelector('style[data-xss-check]');
              if (!styleExists) {
                  var style = document.createElement('style');
                  style.setAttribute('data-xss-check', 'true');
                  style.textContent = '@keyframes xsscheck { 0% { opacity: 1; } 100% { opacity: 0.99; } }';
                  document.head.appendChild(style);
              }
              
              // Find elements with animation event handlers
              var animationHandlers = [
                  'onanimationstart', 'onanimationend', 'onanimationiteration', 'onanimationcancel'
              ];
              
              animationHandlers.forEach(function(handler) {
                  var elements = document.querySelectorAll('[' + handler + ']');
                  Array.prototype.forEach.call(elements, function(el) {
                      // First, try to apply an animation to trigger the handler naturally
                      var currentStyle = el.getAttribute('style') || '';
                      if (currentStyle.indexOf('animation') === -1) {
                          // Apply animation that will trigger the handler
                          el.style.animationName = 'xsscheck';
                          el.style.animationDuration = '0.01s';
                      }
                      
                      // Also dispatch the event directly as a fallback
                      setTimeout(function() {
                          try {
                              var eventName = handler.substring(2); // Remove 'on' prefix
                              var event = document.createEvent('Event');
                              event.initEvent(eventName, true, true);
                              el.dispatchEvent(event);
                          } catch(e) {}
                      }, 100);
                  });
              });

              // Dispatch "focus" event to elements that may have "autofocus" or "onfocus" handlers
              var focusElements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(focusElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });
          });
          
          // Wait for animations to complete and handlers to execute
          setTimeout(function() {
              phantom.exit();
          }, 2000);

      }, 500);
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});
