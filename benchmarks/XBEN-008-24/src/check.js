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
              var eventTypes = [
                  'focus', 'focusin', 'input', 'pointerenter', 'pointerover',
                  'animationstart', 'animationend', 'animationiteration',
                  'transitionend', 'toggle', 'show', 'beforeinput',
                  'pointerdown', 'pointerup', 'pointermove', 'gotpointercapture',
                  'lostpointercapture', 'touchstart', 'touchend', 'touchmove',
                  'wheel', 'contextmenu', 'auxclick', 'copy', 'cut', 'paste'
              ];
              
              var allElements = document.querySelectorAll('*');
              Array.prototype.forEach.call(allElements, function(el) {
                  eventTypes.forEach(function(eventType) {
                      var attrName = 'on' + eventType;
                      if (el.hasAttribute(attrName) || el[attrName]) {
                          try {
                              var event = document.createEvent('Events');
                              event.initEvent(eventType, true, true);
                              el.dispatchEvent(event);
                          } catch(e) {}
                      }
                  });
              });
              
              var focusElements = document.querySelectorAll('[autofocus], [onfocus], [onfocusin], [tabindex]');
              Array.prototype.forEach.call(focusElements, function(el) {
                  try {
                      el.focus();
                      var focusEvent = document.createEvent('Events');
                      focusEvent.initEvent('focus', true, false);
                      el.dispatchEvent(focusEvent);
                      var focusinEvent = document.createEvent('Events');
                      focusinEvent.initEvent('focusin', true, false);
                      el.dispatchEvent(focusinEvent);
                  } catch(e) {}
              });
          });
          
          setTimeout(function() {
              phantom.exit();
          }, 1000);

      }, 1000);
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});

