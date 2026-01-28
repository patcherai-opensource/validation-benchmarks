$(document).ready(function() {
    function fetchDocuments() {
        $.ajax({
            url: '/api/docs',
            method: 'GET',
            success: function(response) {
                let docsList = $('#documents-list');
                docsList.empty();
                
                if (response.documents && response.documents.length > 0) {
                    response.documents.forEach(doc => {
                        docsList.append(`
                            <div class="card doc-card">
                                <div class="card-body">
                                    <h5 class="card-title">${doc.title}</h5>
                                    <p class="card-text">
                                        <small class="text-muted">Space: ${doc.space} | Author: ${doc.author}</small>
                                    </p>
                                </div>
                            </div>
                        `);
                    });
                } else {
                    docsList.html('<p class="text-muted">No documents found.</p>');
                }
            },
            error: function(error) {
                console.log('Error fetching documents:', error);
                $('#documents-list').html('<p class="text-danger">Error loading documents.</p>');
            }
        });
    }

    function searchDocuments(query) {
        $.ajax({
            url: '/api/search?q=' + encodeURIComponent(query),
            method: 'GET',
            success: function(response) {
                let docsList = $('#documents-list');
                docsList.empty();
                
                if (response.suggestions && response.suggestions.length > 0) {
                    response.suggestions.forEach(doc => {
                        docsList.append(`
                            <div class="card doc-card">
                                <div class="card-body">
                                    <h5 class="card-title">${doc.title}</h5>
                                    <p class="card-text">
                                        <small class="text-muted">Space: ${doc.space}</small>
                                    </p>
                                </div>
                            </div>
                        `);
                    });
                } else {
                    docsList.html('<p class="text-muted">No results found.</p>');
                }
            },
            error: function(error) {
                console.log('Error searching:', error);
            }
        });
    }

    // Load documents on page load
    fetchDocuments();

    // Search functionality
    $('#search-btn').click(function() {
        let query = $('#search-input').val();
        if (query) {
            searchDocuments(query);
        } else {
            fetchDocuments();
        }
    });

    $('#search-input').keypress(function(e) {
        if (e.which == 13) {
            $('#search-btn').click();
        }
    });
});
