var system = require('system');
// var json = JSON.parse(system.args[1]);
// var input = json.url;
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
              var focusElements = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(focusElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });
              
              // Dispatch pointer events for elements with pointer event handlers
              // This allows testing CVE-2023-39527 style attacks with onpointerdown etc.
              var pointerEvents = ['pointerdown', 'pointerup', 'pointermove', 'pointerover', 
                                   'pointerout', 'pointerenter', 'pointerleave'];
              var pointerSelectors = pointerEvents.map(function(e) { return '[on' + e + ']'; }).join(', ');
              var pointerElements = document.querySelectorAll(pointerSelectors);
              
              Array.prototype.forEach.call(pointerElements, function(el) {
                  pointerEvents.forEach(function(eventType) {
                      if (el.getAttribute('on' + eventType)) {
                          try {
                              var event = document.createEvent('Events');
                              event.initEvent(eventType, true, true);
                              el.dispatchEvent(event);
                          } catch(e) {}
                      }
                  });
              });
              
              // Also dispatch mouseover events for elements with onmouseover
              var mouseoverElements = document.querySelectorAll('[onmouseover]');
              Array.prototype.forEach.call(mouseoverElements, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('mouseover', true, false);
                  el.dispatchEvent(event);
              });
          });
          
          // Ensure to wait a bit before terminating PhantomJS to allow event handlers to execute
          setTimeout(function() {
              phantom.exit();
          }, 1000); // Adjust timeout as necessary based on observed behavior

      }, 1000); // Initial delay to allow the page to fully load and scripts to initialize
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});

