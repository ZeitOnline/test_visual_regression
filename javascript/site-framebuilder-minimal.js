/**
 * @fileOverview zeit.web.site-framebuilder-minimal module
 * @version  0.1
 */

// A hack for Modernizr and AMD.
// This lets Modernizr be in the <head> and also compatible with other modules.
define( 'modernizr', [], window.Modernizr );

// include requirejs and config first, including path and shim config
require([ 'vendor/require', 'config' ], function() {});

// add required jQuery plugins
// require jQuery first, so we don't have to shim simple plugins
// plugins that require other plugins or libraries must use the shim config
require([
    'jquery',
    'web.site/plugins/jquery.extendfooter'
], function( $, Velocity ) {
    $( '.footer-publisher__more' ).extendFooter();
});
