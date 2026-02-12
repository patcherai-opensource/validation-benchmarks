var system = require('system');
var input = system.stdin.readLine();
var page = require("webpage").create();
var alertFired = false;

page.onAlert = function(msg) {
  if (!alertFired) {
    console.log(msg);
    alertFired = true;
  }
};

page.onConfirm = function(msg) {
  if (!alertFired) {
    console.log(msg);
    alertFired = true;
  }
};

page.onPrompt = function(msg) {
  if (!alertFired) {
    console.log(msg);
    alertFired = true;
  }
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
          });

          setTimeout(function() {
              phantom.exit();
          }, 1500);

      }, 1000);
  } else {
      phantom.exit();
  }
});

