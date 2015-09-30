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
        // to build current sjcl.js, in bower_components/sjcl do
        // $ ./configure --without-all --with-sha1 --with-codecHex --compress=none
        // $ make sjcl.js tidy
        'sjcl': 'libs/sjcl',
        'bxSlider': 'vendor/jquery.bxslider',
        'freewall': 'vendor/freewall',
        'jquery.clarify': 'web.core/plugins/jquery.clarify',
        'jquery.debounce': 'web.core/plugins/jquery.debounce',
        'jquery.inview': 'vendor/jquery.inview'
    },
    // a shim is needed for jQuery Plugins to load
    // add the name or path and an array of required scripts
    shim: {
        'bxSlider': [ 'jquery' ],
        'jquery.clarify': [ 'jquery' ],
        'jquery.debounce': [ 'jquery' ],
        'web.core/plugins/jquery.inlinegallery': [ 'bxSlider', 'jquery', 'modernizr' ],
        'web.magazin/plugins/jquery.backgroundvideo': [ 'jquery', 'modernizr' ],
        'web.site/plugins/jquery.autoclick': [ 'jquery', 'modernizr' ],
        'web.site/plugins/jquery.hpOverlay': [ 'jquery', 'jquery.debounce' ],
        'web.site/plugins/jquery.snapshot': [ 'jquery', 'jquery.inview' ],
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
