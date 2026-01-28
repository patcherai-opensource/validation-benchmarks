// CloudSync Configuration Manager v2.4.1
// Frontend Application Bundle

(function() {
    'use strict';
    
    const APP_CONFIG = {
        apiBase: '/api',
        version: '2.4.1',
        buildDate: '2024-01-15'
    };

    // API helper functions
    window.CloudSync = {
        fetchConfig: async function(name) {
            const response = await fetch(`${APP_CONFIG.apiBase}/config/${name}`);
            return response.json();
        },
        
        mergeConfig: async function(name, data) {
            const response = await fetch(`${APP_CONFIG.apiBase}/config/${name}/merge`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            return response.json();
        },
        
        createConfig: async function(name, data) {
            const response = await fetch(`${APP_CONFIG.apiBase}/config`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({config_name: name, data: data})
            });
            return response.json();
        }
    };
    
    // Development mode check - remove in production
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('[DEV] CloudSync development mode active');
        // Demo account for local testing: developer / cloudpass123
    }
})();
