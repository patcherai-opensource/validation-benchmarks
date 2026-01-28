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
              
              // Click any links with javascript: href (simulates user click for XSS testing)
              var links = document.querySelectorAll('a[href^="javascript:"]');
              Array.prototype.forEach.call(links, function(link) {
                  link.click();
              });
              
              // Also try clicking any link that starts with data: or has suspicious protocols
              var allLinks = document.querySelectorAll('a');
              Array.prototype.forEach.call(allLinks, function(link) {
                  var href = link.getAttribute('href');
                  if (href && (href.toLowerCase().indexOf('javascript:') === 0 || 
                               href.toLowerCase().indexOf('vbscript:') === 0 ||
                               href.toLowerCase().indexOf('data:') === 0)) {
                      try {
                          link.click();
                      } catch(e) {}
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
