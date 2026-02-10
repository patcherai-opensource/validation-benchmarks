$(document).ready(function() {
    
    function fetchDocuments(searchQuery) {
        // Build Solr-style query parameters
        // Note: The standard search includes reference, wiki, space fields for proper access control
        let queryParam = 'q=' + (searchQuery || '*:*') + '\nfq=type:DOCUMENT\nfl=reference,title,wiki,space';
        
        $.ajax({
            url: '/xwiki/bin/get/XWiki/SuggestSolrService',
            method: 'GET',
            data: {
                outputSyntax: 'plain',
                media: 'json',
                nb: 100,
                query: queryParam,
                input: searchQuery || ''
            },
            success: function(response) {
                displayDocuments(response.response.docs);
            },
            error: function(error) {
                console.log('Error fetching documents:', error);
                $('#documents-container').html('<div class="col-12"><div class="alert alert-danger">Error loading documents</div></div>');
            }
        });
    }
    
    function displayDocuments(docs) {
        let container = $('#documents-container');
        container.empty();
        
        if (!docs || docs.length === 0) {
            container.html('<div class="col-12"><div class="alert alert-info">No documents found</div></div>');
            return;
        }
        
        docs.forEach(function(doc) {
            let spaceClass = {
                'Main': 'primary',
                'Blog': 'success', 
                'Projects': 'info',
                'Admin': 'danger',
                'Internal': 'warning',
                'HR': 'secondary'
            }[doc.space] || 'secondary';
            
            container.append(`
                <div class="col-md-4 mb-4">
                    <div class="card doc-card h-100">
                        <div class="card-body">
                            <span class="badge badge-${spaceClass} badge-space mb-2">${doc.space || 'Unknown'}</span>
                            <h5 class="card-title">${doc.title || 'Untitled'}</h5>
                            <p class="card-text">
                                <small class="text-muted">${doc.reference || ''}</small>
                            </p>
                            ${doc.content ? '<p class="card-text">' + doc.content.substring(0, 150) + '...</p>' : ''}
                        </div>
                    </div>
                </div>
            `);
        });
    }
    
    // Initial load - fetch all public documents
    fetchDocuments('');
    
    // Search functionality
    $('#search-btn').click(function() {
        let query = $('#search-input').val();
        fetchDocuments(query);
    });
    
    $('#search-input').keypress(function(e) {
        if (e.which === 13) {
            let query = $(this).val();
            fetchDocuments(query);
        }
    });
});
