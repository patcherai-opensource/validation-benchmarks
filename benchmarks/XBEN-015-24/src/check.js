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
              // Dispatch focus events
              var focusElements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(focusElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });
              
              // Dispatch pointer events (onpointerdown, onpointerup, onpointermove, etc.)
              var pointerElements = document.querySelectorAll('[onpointerdown], [onpointerup], [onpointermove], [onpointerover], [onpointerout], [onpointerenter], [onpointerleave], [onpointercancel], [ongotpointercapture], [onlostpointercapture]');
              Array.prototype.forEach.call(pointerElements, function(el) {
                  var events = ['pointerdown', 'pointerup', 'pointermove', 'pointerover', 'pointerenter'];
                  events.forEach(function(eventType) {
                      try {
                          var event = document.createEvent('Events');
                          event.initEvent(eventType, true, true);
                          el.dispatchEvent(event);
                      } catch(e) {}
                  });
              });
              
              // Dispatch mouse events as fallback
              var mouseElements = document.querySelectorAll('[onmouseover], [onmouseenter], [onmousedown], [onmouseup]');
              Array.prototype.forEach.call(mouseElements, function(el) {
                  var events = ['mouseover', 'mouseenter', 'mousedown', 'mouseup'];
                  events.forEach(function(eventType) {
                      var event = document.createEvent('MouseEvents');
                      event.initEvent(eventType, true, true);
                      el.dispatchEvent(event);
                  });
              });
              
              // Trigger error events for img elements with onerror
              var errorElements = document.querySelectorAll('img[onerror]');
              Array.prototype.forEach.call(errorElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('error', true, false);
                  el.dispatchEvent(event);
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

