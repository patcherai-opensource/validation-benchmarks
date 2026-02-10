jQuery(document).ready(function($) {
    $('#gpi-install-form').on('submit', function(e) {
        e.preventDefault();
        
        var $form = $(this);
        var $submit = $('#gpi-submit');
        var $results = $('#gpi-results');
        var $output = $('#gpi-output');
        
        $submit.prop('disabled', true).text('Installing...');
        $results.hide();
        
        $.ajax({
            url: gpiAjax.ajaxUrl,
            type: 'POST',
            data: {
                action: 'gpi_install_plugin',
                nonce: gpiAjax.nonce,
                plugin_name: $('#plugin_name').val(),
                git_url: $('#git_url').val(),
                branch: $('#branch').val(),
                source: $('#source').val()
            },
            success: function(response) {
                $results.show();
                if (response.success) {
                    $output.html('SUCCESS: ' + response.data.message + '\n\n' + (response.data.output || ''));
                } else {
                    $output.html('ERROR: ' + response.data.message + '\n\n' + (response.data.output || ''));
                }
            },
            error: function(xhr, status, error) {
                $results.show();
                $output.html('AJAX ERROR: ' + error);
            },
            complete: function() {
                $submit.prop('disabled', false).text('Install Plugin');
            }
        });
    });
});
