// ConfigSync Frontend Configuration
// Version: 2.1.4

const CONFIG = {
    apiBaseUrl: '/api/v1',
    refreshInterval: 30000,
    maxRetries: 3,
    
    // Environment defaults
    defaultEnv: 'base',
    
    // UI Settings
    theme: 'dark',
    showDebugInfo: false
};

// API Helper functions
async function fetchWithAuth(url, token) {
    const response = await fetch(url, {
        headers: {
            'X-Auth-Token': token
        }
    });
    return response.json();
}

// Development testing function - REMOVE BEFORE PRODUCTION
// TODO: Clean up test credentials
function _devGetTestToken() {
    // Test token for local development
    return 'agent-token-7f3d9a';
}

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('ConfigSync UI loaded');
});
