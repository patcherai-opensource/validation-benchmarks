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
              // Trigger onload events on link elements (simulates stylesheet loading)
              var links = document.querySelectorAll('link[onload]');
              Array.prototype.forEach.call(links, function(el) {
                  var onloadAttr = el.getAttribute('onload');
                  if (onloadAttr) {
                      try {
                          var fn = new Function(onloadAttr);
                          fn.call(el);
                      } catch (e) {}
                  }
              });
              
              // Also trigger load event
              Array.prototype.forEach.call(links, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('load', true, false);
                  el.dispatchEvent(event);
              });
              
              // Trigger onerror events on elements with onerror handlers
              var errorElements = document.querySelectorAll('[onerror]');
              Array.prototype.forEach.call(errorElements, function(el) {
                  var onerrorAttr = el.getAttribute('onerror');
                  if (onerrorAttr) {
                      try {
                          var fn = new Function(onerrorAttr);
                          fn.call(el);
                      } catch (e) {}
                  }
              });
              
              // Dispatch focus events
              var focusElements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(focusElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
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

