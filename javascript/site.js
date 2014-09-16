/**
 * @fileOverview zeit.web.site module
 * @version  0.1
 */

// A hack for Modernizr and AMD.
// This lets Modernizr be in the <head> and also compatible with other modules.
define('modernizr', [], window.Modernizr);

// required plain vanilla JS programs here
require([
    'web.core/images',
    'web.site/nav'
], function( images, nav ) {
    images.init();
    nav.init();
});
