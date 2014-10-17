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
        'sjcl': 'libs/sjcl', // @Todo: would love to use bower's sjcl, but there is a bug in the current version
        'bxSlider': 'libs/jquery.bxslider',
        'esiparser': 'libs/esiparser',
        'jquery.debounce': 'web.core/plugins/jquery.debounce'
    },
    // a shim is need for jQuery Plugins to load
    // add the name or path and an array of required scripts
    shim: {
        'bxSlider': [ 'jquery' ],
        'jquery.debounce': [ 'jquery' ],
        'web.magazin/plugins/jquery.inlinegallery': [ 'bxSlider', 'jquery' ],
        'web.magazin/plugins/jquery.switchvideo': [ 'jquery' ],
        'web.magazin/plugins/jquery.backgroundvideo': [ 'jquery', 'modernizr' ],
        'web.magazin/plugins/jquery.animatescroll': [ 'jquery' ],
        'web.magazin/plugins/jquery.parseesi': [ 'jquery', 'esiparser' ],
        'web.site/plugins/jquery.togglesearch': [ 'jquery' ],
        'web.site/plugins/jquery.togglenavi': [ 'jquery' ],
        'web.site/plugins/jquery.adaptnav': [ 'jquery' ],
        'sjcl': {
            exports: 'sjcl'
        },
        // to require the script at runtime we must use the full path
        'vendor/freewall': {
            deps: [ 'jquery' ],
            exports: 'freewall'
        }
    }
});
