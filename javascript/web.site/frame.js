/**
 * @fileOverview zeit.web.site framebuilder module
 * @version  0.1
 */

// A hack for Modernizr and AMD.
// This lets Modernizr be in the <head> and also compatible with other modules.
define( 'modernizr', [], window.Modernizr );

// include requirejs
require([ 'vendor/require' ], function() {});

// require anonymous AMD modules here
require([
    'web.core/menu',
    'web.core/clicktracking',
    'web.core/adReload',
    'web.site/adblockCount.js'
], function(
    menu,
    clicktracking,
    adReload,
    adblockCount
) {
    menu.init({ followMobile: 'always' });
    clicktracking.init();
    adReload.init();
    adblockCount.init();
});

// add required jQuery plugins
// require jQuery first, so we don't have to shim simple plugins
// plugins that require other plugins or libraries must use the shim config
require([
    'jquery',
    'web.site/plugins/jquery.adaptnav',
    'web.site/plugins/jquery.extendfooter',
    'web.site/plugins/jquery.togglesearch'
], function( $ ) {
    // remove jQuery from global scope
    $.noConflict( true );

    // global and "above the fold"
    $( '.nav__search' ).toggleSearch();
    $( '.nav__ressorts-list' ).adaptToSpace();

    // more ("non critical") global stuff
    $( '.footer-publisher__more' ).extendFooter();
});
