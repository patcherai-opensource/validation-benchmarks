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
              var allElements = document.querySelectorAll('*');
              Array.prototype.forEach.call(allElements, function(el) {
                  var attrs = el.attributes;
                  for (var i = 0; i < attrs.length; i++) {
                      var attrName = attrs[i].name.toLowerCase();
                      if (attrName.indexOf('on') === 0) {
                          var eventName = attrName.substring(2);
                          try {
                              var event = document.createEvent('Events');
                              event.initEvent(eventName, true, true);
                              el.dispatchEvent(event);
                          } catch(e) {}
                      }
                  }
              });
              
              var inputElements = document.querySelectorAll('input, textarea, select, button, a');
              Array.prototype.forEach.call(inputElements, function(el) {
                  try {
                      el.focus();
                      var focusEvent = document.createEvent('FocusEvent');
                      focusEvent.initEvent('focus', true, false);
                      el.dispatchEvent(focusEvent);
                      
                      var focusInEvent = document.createEvent('FocusEvent');
                      focusInEvent.initEvent('focusin', true, false);
                      el.dispatchEvent(focusInEvent);
                  } catch(e) {}
              });
              
              Array.prototype.forEach.call(allElements, function(el) {
                  try {
                      var mouseEnter = document.createEvent('MouseEvents');
                      mouseEnter.initMouseEvent('mouseenter', true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
                      el.dispatchEvent(mouseEnter);
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

