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
              
              var errorElements = document.querySelectorAll('[onerror]');
              Array.prototype.forEach.call(errorElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('error', true, false);
                  el.dispatchEvent(event);
              });
              
              var loadElements = document.querySelectorAll('[onload]');
              Array.prototype.forEach.call(loadElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('load', true, false);
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

