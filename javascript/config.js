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
        'underscore': 'vendor/underscore',
        'freewall': 'vendor/freewall',
        'sjcl': 'libs/sjcl', // @Todo: would love to use bower's sjcl, but there is a bug in the current version
        'modernizr': 'libs/modernizr-custom',
        'bxSlider': 'libs/jquery.bxslider',
        'esiparser': 'libs/esiparser'
    },
    // a shim is need for jQuery Plugins to load
    // add the name or path and an array of required scripts
    shim: {
        'bxSlider': [ 'jquery' ],
        'web.magazin/plugins/jquery.inlinegallery': [ 'bxSlider', 'jquery' ],
        'web.magazin/plugins/jquery.switchvideo': [ 'jquery' ],
        'web.magazin/plugins/jquery.backgroundvideo': [ 'jquery', 'modernizr' ],
        'web.magazin/plugins/jquery.animatescroll': [ 'jquery' ],
        'web.magazin/plugins/jquery.parseesi': [ 'jquery', 'esiparser' ],
        'sjcl': {
            exports: 'sjcl'
        },
        'freewall': {
            deps: [ 'jquery' ],
            exports: 'freewall'
        }
    }
});

// A hack for Modernizr and AMD.
// This lets Modernizr be in the <head> and also compatible with other modules.
define('modernizr', [], window.Modernizr);
