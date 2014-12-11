/**
 * @fileOverview zeit.web.site module
 * @version  0.1
 */

// A hack for Modernizr and AMD.
// This lets Modernizr be in the <head> and also compatible with other modules.
define('modernizr', [], window.Modernizr);

// required plain vanilla JS programs here
require([
    'web.core/images'
], function( images, nav ) {
    images.init();
});

// add required jQuery-Plugins that are writte with AMD header here
// make a shim of them first
// plugins that require plugins need to make this requirement in the shim-section of config
require([
    'web.site/plugins/jquery.togglesearch',
    'web.site/plugins/jquery.togglenavi',
    'web.site/plugins/jquery.adaptnav',
    'web.site/plugins/jquery.up2dateSignals',
    'web.site/plugins/jquery.scrollup',
    'web.site/plugins/jquery.extendfooter',
    'web.site/plugins/jquery.snapshot'
], function() {
    $( '.main_nav__search' ).toggleSearch();
    $( '.logo_bar__menue' ).toggleNavi();
    $( '.primary-nav' ).adaptToSpace();
    $( 'body[data-page-type=\'centerpage\']' ).up2dateSignals();
    $( '.footer-links__button' ).scrollUp();
    $( '.footer-publisher__more' ).extendFooter();
    $( '.snapshot' ).snapshot();
});
