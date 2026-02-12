/**
 * MLflow UI - Lightweight client-side application
 */
(function() {
    'use strict';

    const API_BASE = '/api/2.0/mlflow';
    let currentExperimentId = null;

    // ==================
    // API Functions
    // ==================

    async function apiCall(endpoint, method, body) {
        const opts = {
            method: method || 'GET',
            headers: { 'Content-Type': 'application/json' }
        };
        if (body) opts.body = JSON.stringify(body);

        const resp = await fetch(API_BASE + endpoint, opts);
        const data = await resp.json();
        if (!resp.ok) {
            throw new Error(data.message || 'API request failed');
        }
        return data;
    }

    // ==================
    // Experiments
    // ==================

    async function loadExperiments() {
        const list = document.getElementById('experiment-list');
        try {
            const data = await apiCall('/experiments/search', 'POST', {});
            const experiments = data.experiments || [];
            list.innerHTML = '';

            if (experiments.length === 0) {
                list.innerHTML = '<div class="loading">No experiments found</div>';
                return;
            }

            experiments.forEach(function(exp) {
                const item = document.createElement('div');
                item.className = 'experiment-item' + (exp.experiment_id === currentExperimentId ? ' active' : '');
                item.innerHTML = '<span class="exp-icon">&#128218;</span>' +
                    '<span class="exp-name">' + escapeHtml(exp.name) + '</span>';
                item.addEventListener('click', function() {
                    selectExperiment(exp.experiment_id);
                });
                list.appendChild(item);
            });
        } catch (e) {
            list.innerHTML = '<div class="loading">Failed to load experiments</div>';
        }
    }

    async function selectExperiment(experimentId) {
        currentExperimentId = experimentId;
        const view = document.getElementById('experiment-view');

        try {
            const data = await apiCall('/experiments/get?experiment_id=' + experimentId, 'GET');
            const exp = data.experiment;

            const runsData = await apiCall('/runs/search', 'POST', {
                experiment_ids: [experimentId]
            });
            const runs = runsData.runs || [];

            let runsHtml = '';
            if (runs.length > 0) {
                runsHtml = '<table class="runs-table"><thead><tr>' +
                    '<th>Run ID</th><th>Status</th><th>Start Time</th><th>Artifact URI</th>' +
                    '</tr></thead><tbody>';
                runs.forEach(function(run) {
                    const info = run.info;
                    const startDate = new Date(info.start_time).toLocaleString();
                    const statusClass = info.status === 'RUNNING' ? 'running' : 'finished';
                    runsHtml += '<tr>' +
                        '<td><code>' + info.run_id.substring(0, 12) + '...</code></td>' +
                        '<td><span class="status-badge ' + statusClass + '">' + info.status + '</span></td>' +
                        '<td>' + startDate + '</td>' +
                        '<td style="font-size:12px;color:#666;">' + escapeHtml(info.artifact_uri) + '</td>' +
                        '</tr>';
                });
                runsHtml += '</tbody></table>';
            } else {
                runsHtml = '<div class="no-runs"><p>No runs recorded yet.</p>' +
                    '<p style="color:#999;font-size:12px;">Use the MLflow API or SDK to log runs to this experiment.</p></div>';
            }

            const creationDate = new Date(exp.creation_time).toLocaleString();

            view.innerHTML = '<div class="experiment-detail">' +
                '<div class="experiment-detail-header">' +
                '<h2>' + escapeHtml(exp.name) + '</h2>' +
                '<div><button class="btn btn-danger btn-sm" onclick="deleteExperiment(\'' + exp.experiment_id + '\')">Delete</button></div>' +
                '</div>' +
                '<div class="experiment-meta">' +
                '<div class="meta-item"><label>Experiment ID</label><span>' + exp.experiment_id + '</span></div>' +
                '<div class="meta-item"><label>Artifact Location</label><span>' + escapeHtml(exp.artifact_location || 'Default') + '</span></div>' +
                '<div class="meta-item"><label>Created</label><span>' + creationDate + '</span></div>' +
                '<div class="meta-item"><label>Lifecycle Stage</label><span>' + exp.lifecycle_stage + '</span></div>' +
                '</div>' +
                '<div class="runs-section"><h3>Runs</h3>' + runsHtml + '</div>' +
                '</div>';

            loadExperiments();
        } catch (e) {
            view.innerHTML = '<div class="empty-state"><h2>Error</h2><p>' + escapeHtml(e.message) + '</p></div>';
        }
    }

    window.deleteExperiment = async function(experimentId) {
        if (!confirm('Are you sure you want to delete this experiment?')) return;
        try {
            await apiCall('/experiments/delete', 'POST', { experiment_id: experimentId });
            currentExperimentId = null;
            document.getElementById('experiment-view').innerHTML =
                '<div class="empty-state"><h2>Experiment deleted</h2></div>';
            loadExperiments();
            showToast('Experiment deleted successfully', 'success');
        } catch (e) {
            showToast('Failed to delete experiment: ' + e.message, 'error');
        }
    };

    // ==================
    // Create Experiment Modal
    // ==================

    function setupModal() {
        const modal = document.getElementById('create-modal');
        const createBtn = document.getElementById('create-experiment-btn');
        const closeBtn = document.getElementById('modal-close');
        const cancelBtn = document.getElementById('modal-cancel');
        const confirmBtn = document.getElementById('modal-create');

        createBtn.addEventListener('click', function() {
            modal.style.display = 'flex';
            document.getElementById('exp-name').value = '';
            document.getElementById('exp-artifact-location').value = '';
            document.getElementById('exp-name').focus();
        });

        closeBtn.addEventListener('click', function() { modal.style.display = 'none'; });
        cancelBtn.addEventListener('click', function() { modal.style.display = 'none'; });

        modal.addEventListener('click', function(e) {
            if (e.target === modal) modal.style.display = 'none';
        });

        confirmBtn.addEventListener('click', async function() {
            const name = document.getElementById('exp-name').value.trim();
            const artifactLocation = document.getElementById('exp-artifact-location').value.trim();

            if (!name) {
                showToast('Experiment name is required', 'error');
                return;
            }

            try {
                const body = { name: name };
                if (artifactLocation) body.artifact_location = artifactLocation;

                const data = await apiCall('/experiments/create', 'POST', body);
                modal.style.display = 'none';
                showToast('Experiment "' + name + '" created successfully', 'success');
                await loadExperiments();
                selectExperiment(data.experiment_id);
            } catch (e) {
                showToast('Failed to create experiment: ' + e.message, 'error');
            }
        });
    }

    // ==================
    // Utilities
    // ==================

    function escapeHtml(str) {
        if (!str) return '';
        var div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function showToast(message, type) {
        var existing = document.querySelector('.toast');
        if (existing) existing.remove();

        var toast = document.createElement('div');
        toast.className = 'toast ' + (type || '');
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(function() {
            toast.style.opacity = '0';
            setTimeout(function() { toast.remove(); }, 300);
        }, 3000);
    }

    // ==================
    // Init
    // ==================

    document.addEventListener('DOMContentLoaded', function() {
        setupModal();
        loadExperiments();
    });
})();
