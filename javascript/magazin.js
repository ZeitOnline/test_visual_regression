/**
 * @fileOverview zeit.web.magazin module
 * @version  0.1
 */

// A hack for Modernizr and AMD.
// This lets Modernizr be in the <head> and also compatible with other modules.
define( 'modernizr', [], window.Modernizr );

// load config first including path and shim config
require([ 'config' ], function() {});

// required plain vanilla JS programs here
// the order in the array and the function names have to correlate
// which is quite disturbing in my book…
require([
    'web.core/images',
    'web.magazin/errors',
    'web.magazin/fontloader-body',
    'web.magazin/main-nav',
    'web.magazin/tabs',
    'web.magazin/comments',
    'web.magazin/sharing',
    'web.magazin/cards',
    'web.magazin/copyrights',
    'web.magazin/photocluster'
], function( images, errors, fontloader, nav, tabs, comments, sharing, cards, copyrights, photocluster ) {
    errors.init();
    fontloader.init();
    nav.init();
    tabs.init();
    comments.init();
    sharing.init();
    cards.init();
    copyrights.init();
    photocluster.init();
    images.init();
});

// add required jQuery plugins
// require jQuery first, so we don't have to shim simple plugins
// plugins that require other plugins or libraries must use the shim config
require([
    'jquery',
    'web.core/plugins/jquery.inlinegallery',
    'web.core/plugins/jquery.referrerCount',
    'web.magazin/plugins/jquery.switchvideo',
    'web.magazin/plugins/jquery.backgroundvideo',
    'web.magazin/plugins/jquery.animatescroll'
], function( $ ) {
    $( window ).referrerCount();
    $( '.inline-gallery' ).inlinegallery();
    $( 'figure[data-video]' ).switchVideo();
    $( 'div[data-backgroundvideo]' ).backgroundVideo();
    $( 'main' ).animateScroll({ selector: '.js-scroll' });
});
