$(document).ready(function() {
    function fetchRecords(filter) {
        $.ajax({
            url: '/api/process',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ filter: filter }),
            success: function(response) {
                let resultsTable = $('#results-table');
                resultsTable.empty();
                
                if (response.error) {
                    resultsTable.append(`<tr><td colspan="3" class="text-danger">${response.error}</td></tr>`);
                    return;
                }
                
                if (response.records && response.records.length > 0) {
                    response.records.forEach(record => {
                        resultsTable.append(`
                            <tr>
                                <td>${record.name}</td>
                                <td><span class="badge badge-info">${record.type}</span></td>
                                <td><pre class="mb-0">${JSON.stringify(record.content, null, 2)}</pre></td>
                            </tr>
                        `);
                    });
                } else {
                    resultsTable.append('<tr><td colspan="3">No records found</td></tr>');
                }
            },
            error: function(xhr) {
                let resultsTable = $('#results-table');
                resultsTable.empty();
                const error = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                resultsTable.append(`<tr><td colspan="3" class="text-danger">${error}</td></tr>`);
            }
        });
    }

    // Load initial records
    fetchRecords({ type: 'public' });

    // Handle form submission
    $('#queryForm').on('submit', function(e) {
        e.preventDefault();
        
        let filter = {};
        const recordType = $('#recordType').val();
        const recordName = $('#recordName').val();
        
        if (recordType) {
            filter.type = recordType;
        }
        if (recordName) {
            filter.name = recordName;
        }
        
        fetchRecords(filter);
    });
});
