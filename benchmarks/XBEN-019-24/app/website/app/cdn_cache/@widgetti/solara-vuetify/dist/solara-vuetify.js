/* solara-vuetify widget bundle - cached from CDN */
(function(root, factory) {
    if (typeof define === 'function' && define.amd) {
        define(['@jupyter-widgets/base', 'ipyvuetify'], factory);
    } else {
        root['solara-vuetify'] = factory(root['@jupyter-widgets/base'], root.ipyvuetify);
    }
}(this, function(base, vuetify) {
    'use strict';
    var version = '1.34.0';
    return { version: version };
}));
