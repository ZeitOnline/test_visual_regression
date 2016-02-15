/**
 * @fileOverview zeit.web.campus module
 * @version  0.1
 */

// A hack for Modernizr and AMD.
// This lets Modernizr be in the <head> and also compatible with other modules.
define( 'modernizr', [], window.Modernizr );

// include requirejs and config first, including path and shim config
require([ 'vendor/require', 'config' ], function() {});

// require anonymous AMD modules here
require([
    'web.core/zeit',
    'web.core/images',
    'web.core/clicktracking'
], function(
    zeit,
    images,
    clicktracking
) {
    images.init();
    clicktracking.init();
    zeit.clearQueue();
});

// add required jQuery plugins
// require jQuery first, so we don't have to shim simple plugins
// plugins that require other plugins or libraries must use the shim config
require([
    'jquery',
    'velocity.ui',
    'web.core/plugins/jquery.scrollIntoView', // plugin used by other plugins
    'web.core/plugins/jquery.animatescroll',
    'web.core/plugins/jquery.referrerCount'
], function( $, Velocity ) {

    $( window ).referrerCount();
    $( '.js-scroll' ).animateScroll();

});
