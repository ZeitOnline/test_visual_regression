/**
 * @fileOverview zeit.web.magazin module
 * @version  0.1
 */

// A hack for Modernizr and AMD.
// This lets Modernizr be in the <head> and also compatible with other modules.
define( 'modernizr', [], window.Modernizr );

// include requirejs and config first, including path and shim config
require([ 'vendor/require', 'config' ], function() {});

// require anonymous AMD modules here
// the order in the array and the function names have to correlate
// which is quite disturbing in my book…
require([
    'web.core/adReload',
    'web.core/images',
    'web.magazin/errors',
    'web.magazin/main-nav',
    'web.magazin/tabs',
    'web.magazin/comments',
    'web.magazin/sharing',
    'web.magazin/cards',
    'web.magazin/photocluster'
], function( adReload, images, errors, nav, tabs, comments, sharing, cards, photocluster ) {
    adReload.init();
    errors.init();
    nav.init();
    tabs.init();
    comments.init();
    sharing.init();
    cards.init();
    photocluster.init();
    images.init();
});

// add required jQuery plugins
// require jQuery first, so we don't have to shim simple plugins
// plugins that require other plugins or libraries must use the shim config
require([
    'jquery',
    'velocity.ui',
    'web.core/plugins/jquery.animatescroll',
    'web.core/plugins/jquery.inlinegallery',
    'web.core/plugins/jquery.picturefill',
    'web.core/plugins/jquery.referrerCount',
    'web.core/plugins/jquery.scrollIntoView', // plugin used by other plugins
    'web.magazin/plugins/jquery.backgroundvideo',
    'web.magazin/plugins/jquery.copyrights',
    'web.magazin/plugins/jquery.switchvideo'
], function( $, Velocity ) {
    $( window ).referrerCount();
    $( '.inline-gallery' ).inlinegallery();
    $( 'figure[data-video]' ).switchVideo();
    $( 'div[data-backgroundvideo]' ).backgroundVideo();
    $.picturefill();
    $( '.js-toggle-copyrights' ).copyrights();
    $( 'main' ).animateScroll({ selector: '.js-scroll' });
});
