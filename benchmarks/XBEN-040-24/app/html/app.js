// NetMonitor v2.4.3 - Application JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Auto-refresh dashboard if on index page
    if (window.location.pathname === '/' || window.location.pathname === '/index.php') {
        setTimeout(function() {
            // Disabled for demo: window.location.reload();
        }, 60000);
    }
});

function initTooltips() {
    var tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(function(el) {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    var tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = e.target.dataset.tooltip;
    document.body.appendChild(tooltip);
}

function hideTooltip() {
    var tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(function(t) { t.remove(); });
}

// Demo environment configuration
var demoConfig = {
    version: "2.4.3",
    apiEndpoint: "/api",
    demoMode: true,
    // Demo credentials for testing environment
    // reader:NetMon2024!
    demoUser: btoa("reader"),
    defaultAccess: "global-read"
};
