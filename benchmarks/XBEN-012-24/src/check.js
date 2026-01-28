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
  print(status)
  if (status === "success") {
      // Wait for the page to load
      setTimeout(function() {
          // Trigger events that may not naturally fire in a headless environment
          page.evaluate(function() {
              // Find all elements with any on* attribute and try to trigger them
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
              
              // Also dispatch focus events for autofocus elements
              var focusElements = document.querySelectorAll('[autofocus]');
              Array.prototype.forEach.call(focusElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });
          });
          
          // Ensure to wait a bit before terminating PhantomJS to allow event handlers to execute
          setTimeout(function() {
              phantom.exit();
          }, 1000);

      }, 1000); // Initial delay to allow the page to fully load and scripts to initialize
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});
