// DataAnnotate Platform JavaScript
(function() {
    'use strict';
    
    // Initialize application
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DataAnnotate Platform v2.1.0 loaded');
        initNavigation();
        initForms();
    });
    
    function initNavigation() {
        // Highlight current page in navigation
        var currentPath = window.location.pathname;
        var navLinks = document.querySelectorAll('.nav-links a');
        navLinks.forEach(function(link) {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }
    
    function initForms() {
        // Add form validation
        var forms = document.querySelectorAll('form');
        forms.forEach(function(form) {
            form.addEventListener('submit', function(e) {
                var inputs = form.querySelectorAll('input[required]');
                var valid = true;
                inputs.forEach(function(input) {
                    if (!input.value.trim()) {
                        valid = false;
                        input.classList.add('error');
                    } else {
                        input.classList.remove('error');
                    }
                });
                if (!valid) {
                    e.preventDefault();
                    alert('Please fill in all required fields');
                }
            });
        });
    }
    
    // API client for labeling operations
    window.DataAnnotateAPI = {
        baseUrl: '/api',
        
        getProjects: function() {
            return fetch(this.baseUrl + '/projects')
                .then(function(response) { return response.json(); });
        },
        
        createProject: function(data) {
            return fetch(this.baseUrl + '/projects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).then(function(response) { return response.json(); });
        }
    };
})();
