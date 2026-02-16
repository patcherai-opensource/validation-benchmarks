var system = require('system');
var input = system.stdin.readLine();

var page = require("webpage").create();

var alertFired = false;

page.onAlert = function(msg) {
  if (!alertFired) {
    alertFired = true;
    console.log(msg);
  }
};

page.onConfirm = function(msg) {
  if (!alertFired) {
    alertFired = true;
    console.log(msg);
  }
};

page.onPrompt = function(msg) {
  if (!alertFired) {
    alertFired = true;
    console.log(msg);
  }
};

page.open(input, function(status) {
  if (status === "success") {
      setTimeout(function() {
          // Dispatch focus events for elements with autofocus or onfocus handlers
          page.evaluate(function() {
              var elements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(elements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });
          });

          // Also check iframes with javascript: URIs and evaluate them
          page.evaluate(function() {
              var iframes = document.querySelectorAll('iframe');
              Array.prototype.forEach.call(iframes, function(iframe) {
                  var src = iframe.getAttribute('src') || '';
                  if (src.indexOf('javascript:') === 0) {
                      try {
                          var code = decodeURIComponent(src.substring(11));
                          eval(code);
                      } catch(e) {}
                  }
              });
          });

          setTimeout(function() {
              phantom.exit();
          }, 2000);

      }, 2000);
  } else {
      phantom.exit();
  }
});
