/**
 * DataLabel Studio - Main Application JavaScript
 * Version 2.4.1
 */

(function() {
    'use strict';

    const DataLabelStudio = {
        config: {
            apiEndpoint: '/api/v1',
            annotationTimeout: 30000,
            maxFileSize: 50 * 1024 * 1024,
        },

        init: function() {
            console.log('DataLabel Studio initializing...');
            this.bindEvents();
            this.loadProjects();
        },

        bindEvents: function() {
            document.querySelectorAll('.project-card').forEach(card => {
                card.addEventListener('click', this.openProject.bind(this));
            });

            const uploadForm = document.getElementById('upload-form');
            if (uploadForm) {
                uploadForm.addEventListener('submit', this.handleUpload.bind(this));
            }
        },

        loadProjects: function() {
            fetch(this.config.apiEndpoint + '/projects')
                .then(response => response.json())
                .then(data => this.renderProjects(data))
                .catch(err => console.error('Failed to load projects:', err));
        },

        renderProjects: function(projects) {
            const container = document.getElementById('projects-container');
            if (!container) return;

            projects.forEach(project => {
                const card = document.createElement('div');
                card.className = 'project-card';
                card.dataset.id = project.id;
                card.innerHTML = `
                    <h3>${project.name}</h3>
                    <p>${project.task_count} tasks</p>
                    <span class="status ${project.status}">${project.status}</span>
                `;
                container.appendChild(card);
            });
        },

        openProject: function(e) {
            const projectId = e.currentTarget.dataset.id;
            window.location.href = `/projects/${projectId}/`;
        },

        handleUpload: function(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            fetch(this.config.apiEndpoint + '/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.loadProjects();
                } else {
                    alert('Upload failed: ' + data.error);
                }
            });
        }
    };

    document.addEventListener('DOMContentLoaded', () => DataLabelStudio.init());
})();
