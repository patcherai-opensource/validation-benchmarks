/* Meridian CMS - Core JavaScript */
(function() {
    'use strict';
    var MeridianCore = {
        version: '12.4.7',
        init: function() {
            this.initNavigation();
        },
        initNavigation: function() {
            var nav = document.querySelector('.main-nav');
            if (!nav) return;
            var links = nav.querySelectorAll('a');
            for (var i = 0; i < links.length; i++) {
                if (links[i].href === window.location.href) {
                    links[i].classList.add('active');
                }
            }
        }
    };
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() { MeridianCore.init(); });
    } else {
        MeridianCore.init();
    }
})();
