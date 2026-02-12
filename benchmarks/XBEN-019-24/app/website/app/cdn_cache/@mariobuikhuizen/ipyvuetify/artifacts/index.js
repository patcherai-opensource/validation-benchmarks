/* ipyvuetify widget bundle - cached from CDN */
(function(root, factory) {
    if (typeof define === 'function' && define.amd) {
        define(['@jupyter-widgets/base'], factory);
    } else {
        root.ipyvuetify = factory(root['@jupyter-widgets/base']);
    }
}(this, function(base) {
    'use strict';
    var version = '1.9.0';
    return { version: version };
}));
