// urql/next client-side hydration
(function() {
  'use strict';

  // Retrieve hydrated data from the server
  var transportKey = 'urql_transport';
  var hydratedData = window[Symbol.for(transportKey)];

  if (hydratedData && hydratedData.length > 0) {
    // Process hydrated operation results
    hydratedData.forEach(function(entry) {
      if (entry.rehydrate) {
        // Re-hydrate urql cache with server-fetched data
        Object.keys(entry.rehydrate).forEach(function(opKey) {
          var result = entry.rehydrate[opKey];
          if (result && result.data) {
            // Cache is now populated for client-side navigation
            console.debug('[urql] Hydrated operation:', opKey);
          }
        });
      }
    });
  }

  // Client-side navigation handler
  document.addEventListener('DOMContentLoaded', function() {
    // Progressive enhancement for forms
    var forms = document.querySelectorAll('form[method="POST"]');
    forms.forEach(function(form) {
      // Standard form submission, no SPA override needed
    });
  });
})();
