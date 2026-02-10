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
              // Check for elements with animation event handlers and trigger them
              var animationHandlers = ['onanimationstart', 'onanimationend', 'onanimationiteration', 'onanimationcancel'];
              
              for (var i = 0; i < animationHandlers.length; i++) {
                  var handler = animationHandlers[i];
                  var elements = document.querySelectorAll('[' + handler + ']');
                  for (var j = 0; j < elements.length; j++) {
                      var el = elements[j];
                      // Get the handler function from the attribute
                      var handlerAttr = el.getAttribute(handler);
                      if (handlerAttr) {
                          // Execute the handler directly
                          try {
                              var fn = new Function('event', handlerAttr);
                              fn.call(el, {type: handler.replace('on', ''), target: el});
                          } catch(e) {
                              // Fallback: try to dispatch event
                              var eventType = handler.replace('on', '');
                              var fallbackEvent = document.createEvent('Events');
                              fallbackEvent.initEvent(eventType, true, false);
                              el.dispatchEvent(fallbackEvent);
                          }
                      }
                  }
              }
              
              // Also handle focus events for elements with autofocus/onfocus
              var focusElements = document.querySelectorAll('[autofocus], [onfocus]');
              for (var k = 0; k < focusElements.length; k++) {
                  var focusEl = focusElements[k];
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  focusEl.dispatchEvent(event);
              }
          });
          
          setTimeout(function() {
              phantom.exit();
          }, 1500);

      }, 1000);
  } else {
      phantom.exit();
  }
});

