var system = require('system');
var input = system.stdin.readLine();

var page = require("webpage").create();

var alertFired = false;

page.onAlert = function(msg) {
  if (!alertFired) {
    console.log(msg);
    alertFired = true;
  }
};

page.onConfirm = function(msg) {
  if (!alertFired) {
    console.log(msg);
    alertFired = true;
  }
};

page.onPrompt = function(msg) {
  if (!alertFired) {
    console.log(msg);
    alertFired = true;
  }
};

page.open(input, function(status) {
  if (status === "success") {
      // Wait for page to fully load, scripts to execute, and iframes to initialize
      setTimeout(function() {
          phantom.exit();
      }, 3000);
  } else {
      console.log("Failed to load the page.");
      phantom.exit();
  }
});
