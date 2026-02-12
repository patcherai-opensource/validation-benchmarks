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
              // Dispatch events on interactive elements
              var allElements = document.querySelectorAll('*');
              Array.prototype.forEach.call(allElements, function(el) {
                  var attrs = el.attributes;
                  if (!attrs) return;
                  for (var i = 0; i < attrs.length; i++) {
                      var name = attrs[i].name.toLowerCase();
                      if (name.indexOf('on') === 0 && name.length > 2) {
                          var eventName = name.substring(2);
                          try {
                              var event = document.createEvent('Events');
                              event.initEvent(eventName, true, true);
                              el.dispatchEvent(event);
                          } catch(e) {}
                      }
                  }
              });

              // Handle broken image resources
              var images = document.querySelectorAll('img');
              Array.prototype.forEach.call(images, function(img) {
                  if (!img.complete || img.naturalWidth === 0) {
                      var event = document.createEvent('Events');
                      event.initEvent('error', true, true);
                      img.dispatchEvent(event);
                  }
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

