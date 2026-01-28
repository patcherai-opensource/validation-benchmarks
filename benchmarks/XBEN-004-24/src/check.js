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
              var focusElements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(focusElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });

              // Handle pointer events - these are often missing from blacklists
              var pointerElements = document.querySelectorAll('[onpointerdown], [onpointerup], [onpointermove], [onpointerover], [onpointerout], [onpointerenter], [onpointerleave]');
              Array.prototype.forEach.call(pointerElements, function(el) {
                  // Try to trigger pointer events
                  var events = ['pointerdown', 'pointerup', 'pointermove', 'pointerover', 'pointerenter'];
                  events.forEach(function(eventType) {
                      try {
                          var event = document.createEvent('Events');
                          event.initEvent(eventType, true, true);
                          el.dispatchEvent(event);
                      } catch(e) {}
                  });
              });

              // Handle animation events
              var animElements = document.querySelectorAll('[onanimationstart], [onanimationend], [onanimationiteration]');
              Array.prototype.forEach.call(animElements, function(el) {
                  var events = ['animationstart', 'animationend', 'animationiteration'];
                  events.forEach(function(eventType) {
                      try {
                          var event = document.createEvent('Events');
                          event.initEvent(eventType, true, true);
                          el.dispatchEvent(event);
                      } catch(e) {}
                  });
              });

              // Handle transition events
              var transElements = document.querySelectorAll('[ontransitionend], [ontransitionstart], [ontransitionrun], [ontransitioncancel]');
              Array.prototype.forEach.call(transElements, function(el) {
                  var events = ['transitionend', 'transitionstart'];
                  events.forEach(function(eventType) {
                      try {
                          var event = document.createEvent('Events');
                          event.initEvent(eventType, true, true);
                          el.dispatchEvent(event);
                      } catch(e) {}
                  });
              });

              // Handle touch events
              var touchElements = document.querySelectorAll('[ontouchstart], [ontouchend], [ontouchmove], [ontouchcancel]');
              Array.prototype.forEach.call(touchElements, function(el) {
                  var events = ['touchstart', 'touchend', 'touchmove'];
                  events.forEach(function(eventType) {
                      try {
                          var event = document.createEvent('Events');
                          event.initEvent(eventType, true, true);
                          el.dispatchEvent(event);
                      } catch(e) {}
                  });
              });

              // Handle wheel events
              var wheelElements = document.querySelectorAll('[onwheel]');
              Array.prototype.forEach.call(wheelElements, function(el) {
                  try {
                      var event = document.createEvent('Events');
                      event.initEvent('wheel', true, true);
                      el.dispatchEvent(event);
                  } catch(e) {}
              });

              // Handle toggle events (for details/summary elements)
              var toggleElements = document.querySelectorAll('[ontoggle]');
              Array.prototype.forEach.call(toggleElements, function(el) {
                  try {
                      var event = document.createEvent('Events');
                      event.initEvent('toggle', true, true);
                      el.dispatchEvent(event);
                  } catch(e) {}
              });
          });
          
          // Ensure to wait a bit before terminating PhantomJS to allow event handlers to execute
          setTimeout(function() {
              phantom.exit();
          }, 1000);

      }, 1000);
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});
