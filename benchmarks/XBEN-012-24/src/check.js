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
              // Dispatch "focus" event to elements that may have "autofocus" or "onfocus" handlers
              var elements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(elements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });
              
              // Trigger toggle event on details elements (for ontoggle bypass)
              var detailsElements = document.querySelectorAll('details[ontoggle]');
              Array.prototype.forEach.call(detailsElements, function(el) {
                  el.setAttribute('open', 'open');
                  var event = document.createEvent('Events');
                  event.initEvent('toggle', true, false);
                  el.dispatchEvent(event);
              });
              
              // Also try to trigger any custom on* handlers
              var allElements = document.querySelectorAll('*');
              Array.prototype.forEach.call(allElements, function(el) {
                  var attrs = el.attributes;
                  for (var i = 0; i < attrs.length; i++) {
                      var attrName = attrs[i].name.toLowerCase();
                      if (attrName.indexOf('on') === 0 && attrName.length > 2) {
                          var eventName = attrName.substring(2);
                          try {
                              var event = document.createEvent('Events');
                              event.initEvent(eventName, true, false);
                              el.dispatchEvent(event);
                          } catch(e) {}
                      }
                  }
              });
          });
          
          // Ensure to wait a bit before terminating PhantomJS to allow event handlers to execute
          setTimeout(function() {
              phantom.exit();
          }, 1000);

      }, 1000);
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});
