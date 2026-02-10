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
              
              var links = document.querySelectorAll('a[href]');
              Array.prototype.forEach.call(links, function(link) {
                  var href = link.getAttribute('href');
                  if (href && href.toLowerCase().indexOf('javascript:') === 0) {
                      try {
                          link.click();
                      } catch(e) {}
                  }
              });
              
              var clickables = document.querySelectorAll('[onclick]');
              Array.prototype.forEach.call(clickables, function(el) {
                  var event = document.createEvent('MouseEvents');
                  event.initEvent('click', true, true);
                  el.dispatchEvent(event);
              });
              
              var mouseoverables = document.querySelectorAll('[onmouseover]');
              Array.prototype.forEach.call(mouseoverables, function(el) {
                  var event = document.createEvent('MouseEvents');
                  event.initEvent('mouseover', true, true);
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

