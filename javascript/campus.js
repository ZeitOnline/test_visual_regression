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
    'web.core/clicktracking',
    'web.core/triggeredEventTracking',
    'web.core/adReload',
    'web.core/menu',
    'web.core/comments',
    'web.core/articledate'
], function(
    zeit,
    images,
    clicktracking,
    triggeredEventTracking,
    adReload,
    menu,
    comments,
    articledate
) {
    var article = document.getElementById( 'js-article' );

    images.init();
    menu.init();
    clicktracking.init();
    triggeredEventTracking.init();
    adReload.init();
    zeit.clearQueue();

    if ( article ) {
        comments.init();
        articledate.init();
    }
});

// add required jQuery plugins
// require jQuery first, so we don't have to shim simple plugins
// plugins that require other plugins or libraries must use the shim config
require([
    'jquery',
    'velocity.ui',
    'web.core/plugins/jquery.scrollIntoView', // plugin used by other plugins
    'web.core/plugins/jquery.animatescroll',
    'web.core/plugins/jquery.toggleRegions',
    'web.core/plugins/jquery.infobox',
    'web.core/plugins/jquery.inlinegallery',
    'web.core/plugins/jquery.imageCopyrightFooter',
    'web.core/plugins/jquery.referrerCount',
    'web.core/plugins/jquery.countFormchars',
    'web.core/plugins/jquery.notifications'
], function( $, Velocity ) {
    var pageType = document.body.getAttribute( 'data-page-type' ),
        main = $( '#main' );

    // remove jQuery from global scope
    $.noConflict( true );

    $( window ).referrerCount();
    $( '.js-scroll' ).animateScroll();

    switch ( pageType ) {
        case 'article':
            main.find( '.js-infobox' ).infobox();
            main.find( '.article-toc' ).toggleRegions();
            main.find( '.comment-section' ).countFormchars();

        /* falls through */
        case 'gallery':
            main.find( '.js-gallery' ).inlinegallery();
    }

    $( '.js-image-copyright-footer' ).imageCopyrightFooter();
    $( '.notifications' ).notifications();

});
