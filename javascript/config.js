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
        'freewall': 'vendor/freewall',
        'jquery.clarify': 'web.core/plugins/jquery.clarify',
        'jquery.debounce': 'web.core/plugins/jquery.debounce',
        'jquery.inview': 'vendor/jquery.inview',
        'video': 'web.site/video/video'
    },
    // a shim is need for jQuery Plugins to load
    // add the name or path and an array of required scripts
    shim: {
        'bxSlider': [ 'jquery' ],
        'jquery.clarify': [ 'jquery', 'require' ],
        'jquery.debounce': [ 'jquery' ],
        'web.core/plugins/jquery.referrerCount': [ 'jquery' ],
        'web.magazin/plugins/jquery.animatescroll': [ 'jquery' ],
        'web.magazin/plugins/jquery.backgroundvideo': [ 'jquery', 'modernizr' ],
        'web.magazin/plugins/jquery.inlinegallery': [ 'bxSlider', 'jquery' ],
        'web.magazin/plugins/jquery.parseesi': [ 'jquery', 'esiparser' ],
        'web.magazin/plugins/jquery.switchvideo': [ 'jquery' ],
        'web.site/plugins/jquery.adaptnav': [ 'jquery' ],
        'web.site/plugins/jquery.extendfooter': [ 'jquery' ],
        'web.site/plugins/jquery.scrollup': [ 'jquery' ],
        'web.site/plugins/jquery.selectNav': [ 'jquery' ],
        'web.site/plugins/jquery.snapshot': [ 'jquery', 'jquery.inview' ],
        'web.site/plugins/jquery.toggleBeta': [ 'jquery' ],
        'web.site/plugins/jquery.togglenavi': [ 'jquery' ],
        'web.site/plugins/jquery.togglesearch': [ 'jquery' ],
        'sjcl': {
            exports: 'sjcl'
        },
        'freewall': {
            deps: [ 'jquery' ],
            exports: 'freewall'
        }
    }
});
