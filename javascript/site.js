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

// add required jQuery-Plugins that are writte with AMD header here
// make a shim of them first
// plugins that require plugins need to make this requirement in the shim-section of config
require([
    'web.site/plugins/jquery.togglesearch',
    'web.site/plugins/jquery.togglenavi',
    'web.site/plugins/jquery.adaptnav'
], function() {
    $( '.main_nav__search' ).toggleSearch();
    $( '.logo_bar__menue' ).toggleNavi();
    $( '.primary-nav' ).adaptToSpace();
});
