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
          // Process the page: resolve URLs from href/src attributes and
          // execute any javascript: protocol URLs (simulating browser behavior)
          page.evaluate(function() {
              // Helper: resolve a URL by reading the browser's computed property
              function processJsUrl(resolvedUrl) {
                  if (!resolvedUrl) return;
                  // Normalize: strip control chars the same way browsers do
                  var cleaned = resolvedUrl.replace(/[\t\r\n]/g, '');
                  if (cleaned.toLowerCase().indexOf('javascript:') === 0) {
                      var code = cleaned.substring('javascript:'.length);
                      try {
                          eval(decodeURIComponent(code));
                      } catch(e) {
                          try { eval(code); } catch(e2) {}
                      }
                  }
              }

              // Check anchor tags
              var links = document.querySelectorAll('a[href]');
              Array.prototype.forEach.call(links, function(el) {
                  processJsUrl(el.href);
                  processJsUrl(el.getAttribute('href'));
              });

              // Check iframes
              var iframes = document.querySelectorAll('iframe[src]');
              Array.prototype.forEach.call(iframes, function(el) {
                  processJsUrl(el.src);
                  processJsUrl(el.getAttribute('src'));
              });
          });

          setTimeout(function() {
              phantom.exit();
          }, 2000);
      }, 1000);
  } else {
      phantom.exit();
  }
});

