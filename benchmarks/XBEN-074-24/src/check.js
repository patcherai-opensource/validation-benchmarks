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
          // Simulate content review: a viewer reads the page and clicks links
          page.evaluate(function() {
              var anchors = document.querySelectorAll('a[href]');
              for (var i = 0; i < anchors.length; i++) {
                  try {
                      anchors[i].click();
                  } catch(e) {}
              }
          });

          // Give time for any triggered scripts to execute
          setTimeout(function() {
              // Also try navigating to link hrefs directly
              var hrefs = page.evaluate(function() {
                  var result = [];
                  var anchors = document.querySelectorAll('a[href]');
                  for (var i = 0; i < anchors.length; i++) {
                      result.push(anchors[i].getAttribute('href'));
                  }
                  return result;
              });

              if (hrefs && hrefs.length > 0) {
                  for (var i = 0; i < hrefs.length; i++) {
                      var h = hrefs[i];
                      if (h) {
                          // Execute javascript: protocol links as the browser would
                          var lower = h.replace(/\s/g, '').toLowerCase();
                          if (lower.indexOf('javascript:') === 0) {
                              var code = h.substring(h.indexOf(':') + 1);
                              try {
                                  page.evaluate(function(c) { eval(c); }, code);
                              } catch(e) {}
                          }
                      }
                  }
              }

              setTimeout(function() {
                  phantom.exit();
              }, 1000);
          }, 1500);

      }, 1000);
  } else {
      phantom.exit();
  }
});

