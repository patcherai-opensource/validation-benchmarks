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
      // Wait for the page to fully load and scripts to execute
      setTimeout(function() {
          // Trigger load-related events for images and other media
          page.evaluate(function() {
              // Trigger error events on images that failed to load
              var imgs = document.querySelectorAll('img');
              Array.prototype.forEach.call(imgs, function(img) {
                  if (!img.complete || img.naturalWidth === 0) {
                      var event = document.createEvent('Events');
                      event.initEvent('error', true, false);
                      img.dispatchEvent(event);
                  }
              });

              // Trigger focus events on elements with autofocus
              var focusEls = document.querySelectorAll('[autofocus], [onfocus]');
              Array.prototype.forEach.call(focusEls, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('focus', true, false);
                  el.dispatchEvent(event);
              });

              // Trigger mouseover on elements with onmouseover
              var hoverEls = document.querySelectorAll('[onmouseover]');
              Array.prototype.forEach.call(hoverEls, function(el) {
                  var event = document.createEvent('Events');
                  event.initEvent('mouseover', true, false);
                  el.dispatchEvent(event);
              });
          });
          
          setTimeout(function() {
              phantom.exit();
          }, 1500);

      }, 1000);
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});
