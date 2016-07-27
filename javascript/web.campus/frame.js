/**
 * @fileOverview zeit.web.campus framebuilder module
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
    'web.core/adReload'
], function(
    menu,
    clicktracking,
    adReload
) {
    menu.init();
    clicktracking.init();
    adReload.init();
});

// remove jQuery from global scope
require([ 'jquery' ], function( $ ) {
    $.noConflict( true );
});
