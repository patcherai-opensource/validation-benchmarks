/* jupyter-widgets base bundle - cached from CDN */
(function(root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else {
        root['@jupyter-widgets/base'] = factory();
    }
}(this, function() {
    'use strict';
    var version = '8.1.1';
    return { version: version };
}));
