$(document).ready(function() {
    // Load wiki spaces
    function loadSpaces() {
        $.ajax({
            url: '/wiki/spaces',
            method: 'GET',
            success: function(response) {
                let spacesList = $('#spaces-list');
                spacesList.empty();
                response.spaces.forEach(space => {
                    spacesList.append(`<li><a href="/wiki/bin/view/${space}/Welcome">${space}</a></li>`);
                });
            },
            error: function(error) {
                console.log('Error loading spaces:', error);
            }
        });
    }

    // Search documents
    function searchDocuments(query) {
        $.ajax({
            url: '/wiki/api/search',
            method: 'GET',
            data: { q: query, limit: 20 },
            success: function(response) {
                let docsList = $('#documents-list');
                docsList.empty();
                if (response.results.length === 0) {
                    docsList.append('<p class="text-muted">No documents found.</p>');
                    return;
                }
                response.results.forEach(doc => {
                    docsList.append(`
                        <div class="doc-card">
                            <h5><a href="/wiki/bin/view/${doc.space}/${doc.title}">${doc.title}</a></h5>
                            <span class="space-badge">${doc.space}</span>
                            <p class="mt-2 mb-0 text-muted">${doc.snippet}...</p>
                        </div>
                    `);
                });
            },
            error: function(error) {
                console.log('Error searching documents:', error);
            }
        });
    }

    // Load initial data
    loadSpaces();
    searchDocuments('');

    // Search button click handler
    $('#search-btn').click(function() {
        let query = $('#search-input').val();
        searchDocuments(query);
    });

    // Search on enter key
    $('#search-input').keypress(function(e) {
        if (e.which === 13) {
            let query = $(this).val();
            searchDocuments(query);
        }
    });
});
