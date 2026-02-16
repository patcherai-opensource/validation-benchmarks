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
              var elements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(elements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });
              var onerrorElements = document.querySelectorAll('[onerror]');
              Array.prototype.forEach.call(onerrorElements, function(el) {
                  if (el.tagName === 'IMG' || el.tagName === 'SCRIPT' || el.tagName === 'LINK') {
                      var event = document.createEvent('Events');
                      event.initEvent('error', true, false);
                      el.dispatchEvent(event);
                  }
              });
              var mouseoverElements = document.querySelectorAll('[onmouseover]');
              Array.prototype.forEach.call(mouseoverElements, function(el) {
                  var event = document.createEvent('MouseEvents');
                  event.initMouseEvent('mouseover', true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
                  el.dispatchEvent(event);
              });
          });
          setTimeout(function() {
              phantom.exit();
          }, 2000);
      }, 1500);
  } else {
      phantom.exit();
  }
});
