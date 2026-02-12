$(document).ready(function() {
    // Toggle sidebar on mobile
    $('#sidebarToggle').on('click', function(e) {
        e.preventDefault();
        $('body').toggleClass('sidebar-toggled');
        $('.sidebar').toggleClass('toggled');
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert-dismissible').alert('close');
    }, 5000);
});
