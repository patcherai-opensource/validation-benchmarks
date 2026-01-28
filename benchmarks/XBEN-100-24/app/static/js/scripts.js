$(document).ready(function() {
    function fetchWebhooks() {
        $.ajax({
            url: '/api/webhooks',
            method: 'GET',
            success: function(response) {
                let webhookTable = $('#webhook-table');
                webhookTable.empty();
                
                if (response.webhooks && response.webhooks.length > 0) {
                    response.webhooks.forEach(function(webhook) {
                        let statusClass = 'status-' + webhook.status;
                        webhookTable.append(`
                            <tr>
                                <td><strong>${webhook.name}</strong></td>
                                <td class="webhook-url">${webhook.url}</td>
                                <td><span class="${statusClass}">${webhook.status}</span></td>
                                <td>
                                    <button class="btn btn-sm btn-info view-btn" data-id="${webhook.id}">View</button>
                                    <button class="btn btn-sm btn-success trigger-btn" data-id="${webhook.id}">Trigger</button>
                                </td>
                            </tr>
                        `);
                    });
                } else {
                    webhookTable.append('<tr><td colspan="4" class="text-center">No webhooks registered</td></tr>');
                }
            },
            error: function(error) {
                console.error('Error fetching webhooks:', error);
                $('#webhook-table').html('<tr><td colspan="4" class="text-center text-danger">Error loading webhooks</td></tr>');
            }
        });
    }

    // Load webhooks on page load
    fetchWebhooks();

    // View webhook details
    $(document).on('click', '.view-btn', function() {
        let webhookId = $(this).data('id');
        $.ajax({
            url: '/api/webhooks/' + webhookId,
            method: 'GET',
            success: function(response) {
                alert('Webhook Details:\n' + JSON.stringify(response.webhook, null, 2));
            },
            error: function(error) {
                alert('Error: ' + (error.responseJSON ? error.responseJSON.error : 'Unknown error'));
            }
        });
    });

    // Trigger webhook
    $(document).on('click', '.trigger-btn', function() {
        let webhookId = $(this).data('id');
        $.ajax({
            url: '/api/trigger',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                webhook_id: webhookId,
                payload: { test: true, timestamp: new Date().toISOString() }
            }),
            success: function(response) {
                alert('Trigger Response:\n' + JSON.stringify(response, null, 2));
            },
            error: function(error) {
                alert('Error: ' + (error.responseJSON ? error.responseJSON.error : 'Unknown error'));
            }
        });
    });
});
