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
              var allElements = document.querySelectorAll('*');
              Array.prototype.forEach.call(allElements, function(el) {
                  var attrs = el.attributes;
                  for (var i = 0; i < attrs.length; i++) {
                      var name = attrs[i].name.toLowerCase();
                      if (name.indexOf('on') === 0 && name.length > 2) {
                          var evtName = name.substring(2);
                          try {
                              var event = document.createEvent('Events');
                              event.initEvent(evtName, true, true);
                              el.dispatchEvent(event);
                          } catch(e) {}
                          if (typeof el[name] === 'function') {
                              try { el[name](); } catch(e) {}
                          } else {
                              try {
                                  var code = el.getAttribute(name) || el.getAttribute(attrs[i].name);
                                  if (code) {
                                      var fn = new Function('event', code);
                                      fn.call(el);
                                  }
                              } catch(e) {}
                          }
                      }
                  }
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
