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
              // Helper function to dispatch events
              function dispatchEvent(el, eventName) {
                  var event = document.createEvent('Events');
                  event.initEvent(eventName, true, false);
                  el.dispatchEvent(event);
              }
              
              // Dispatch "focus" and "focusin" events to elements with focus-related handlers
              var focusElements = document.querySelectorAll('[autofocus], [onfocus], [onfocusin], [onfocusout]');
              Array.prototype.forEach.call(focusElements, function(el) {
                  dispatchEvent(el, 'focus');
                  dispatchEvent(el, 'focusin');
                  dispatchEvent(el, 'focusout');
              });
              
              // Dispatch animation events to elements with animation handlers
              // These are event handlers often missed by incomplete blacklists (CVE-inspired)
              var animationElements = document.querySelectorAll('[onanimationstart], [onanimationend], [onanimationiteration]');
              Array.prototype.forEach.call(animationElements, function(el) {
                  dispatchEvent(el, 'animationstart');
                  dispatchEvent(el, 'animationend');
                  dispatchEvent(el, 'animationiteration');
              });
              
              // Dispatch transition events
              var transitionElements = document.querySelectorAll('[ontransitionend], [ontransitionstart], [ontransitionrun]');
              Array.prototype.forEach.call(transitionElements, function(el) {
                  dispatchEvent(el, 'transitionend');
                  dispatchEvent(el, 'transitionstart');
                  dispatchEvent(el, 'transitionrun');
              });
              
              // Dispatch pointer events
              var pointerElements = document.querySelectorAll('[onpointerdown], [onpointerup], [onpointermove], [onpointerover], [onpointerout], [onpointerenter], [onpointerleave]');
              Array.prototype.forEach.call(pointerElements, function(el) {
                  dispatchEvent(el, 'pointerdown');
                  dispatchEvent(el, 'pointerup');
                  dispatchEvent(el, 'pointerover');
                  dispatchEvent(el, 'pointerenter');
              });
              
              // Dispatch touch events (for mobile bypass scenarios)
              var touchElements = document.querySelectorAll('[ontouchstart], [ontouchend], [ontouchmove]');
              Array.prototype.forEach.call(touchElements, function(el) {
                  dispatchEvent(el, 'touchstart');
                  dispatchEvent(el, 'touchend');
              });
              
              // Dispatch auxclick event (right-click alternative)
              var auxElements = document.querySelectorAll('[onauxclick]');
              Array.prototype.forEach.call(auxElements, function(el) {
                  dispatchEvent(el, 'auxclick');
              });
              
              // Dispatch show event (for context menus)
              var showElements = document.querySelectorAll('[onshow]');
              Array.prototype.forEach.call(showElements, function(el) {
                  dispatchEvent(el, 'show');
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

