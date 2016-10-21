/**
 * @fileOverview Require.js Config File
 * @version  0.1
 */

// configuration section for require js
require.config({
    // Require.js allows us to configure shortcut alias
    // e.g. if you'll require jQuery later, you can refer to it as 'jquery'
    paths: {
        'jquery': 'vendor/jquery',
        'picturefill': 'vendor/picturefill',
        'velocity': 'vendor/velocity',
        'velocity.ui': 'vendor/velocity.ui',
        'bxSlider': 'web.core/plugins/jquery.bxslider',
        'freewall': 'vendor/freewall',
        'jquery.clarify': 'web.core/plugins/jquery.clarify',
        'jquery.debounce': 'web.core/plugins/jquery.debounce',
        'jquery.throttle': 'web.core/plugins/jquery.throttle',
        'jquery.inview': 'vendor/jquery.inview'
    },
    // a shim is needed for jQuery Plugins to load
    // add the name or path and an array of required scripts
    shim: {
        'bxSlider': [ 'jquery' ],
        'jquery.clarify': [ 'jquery' ],
        'jquery.debounce': [ 'jquery' ],
        'jquery.throttle': [ 'jquery' ],
        'web.core/plugins/jquery.inlinegallery': [ 'bxSlider', 'jquery', 'modernizr', 'web.core/zeit' ],
        'web.core/plugins/jquery.toggleRegions': [ 'jquery', 'jquery.debounce' ],
        'web.magazin/plugins/jquery.backgroundvideo': [ 'jquery', 'modernizr' ],
        'web.site/plugins/jquery.autoclick': [ 'jquery', 'modernizr' ],
        'web.site/plugins/jquery.fixPosition': [ 'jquery', 'jquery.throttle' ],
        'web.site/plugins/jquery.hpOverlay': [ 'jquery', 'jquery.debounce' ],
        'web.site/plugins/jquery.togglesearch': [ 'jquery', 'jquery.debounce' ],
        'freewall': {
            deps: [ 'jquery' ],
            exports: 'freewall'
        },
        'velocity': {
            deps: [ 'jquery' ]
        },
        'velocity.ui': {
            deps: [ 'velocity' ]
        }
    }
});
