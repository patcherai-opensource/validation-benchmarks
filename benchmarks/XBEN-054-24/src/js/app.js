// MediaShare Pro v2.4.1 - Client Application
(function() {
    'use strict';
    
    const CONFIG = {
        apiBase: '/api',
        maxFileSize: 5242880,
        supportedTypes: ['image/png', 'image/jpeg', 'image/gif', 'application/pdf', 'video/mp4']
    };
    
    function initApp() {
        console.log('MediaShare Pro initialized');
        setupEventHandlers();
    }
    
    function setupEventHandlers() {
        const uploadForm = document.querySelector('form[enctype="multipart/form-data"]');
        if (uploadForm) {
            uploadForm.addEventListener('submit', validateUpload);
        }
    }
    
    function validateUpload(e) {
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            if (file.size > CONFIG.maxFileSize) {
                alert('File size exceeds maximum allowed (5MB)');
                e.preventDefault();
                return false;
            }
        }
        return true;
    }
    
    window.addEventListener('DOMContentLoaded', initApp);
})();
