
var $ = require( 'jquery' ),
    zeit = require( 'web.core/zeit' ),
    images = require( 'web.core/images' ),
    clicktracking = require( 'web.core/clicktracking' ),
    triggeredEventTracking = require( 'web.core/triggeredEventTracking' ),
    visibilityTracking = require( 'web.core/visibilityTracking' ),
    adReload = require( 'web.core/adReload' ),
    menu = require( 'web.core/menu' ),
    comments = require( 'web.core/comments' ),
    articledate = require( 'web.core/articledate' ),
    saveGetToCookie = require( 'web.core/saveGetToCookie' ),
    article = document.getElementById( 'js-article' ),
    pageType = document.body.getAttribute( 'data-page-type' ),
    main = $( '#main' );

// remove jQuery from global scope (needles with node/webpack)
// $.noConflict( true );

// initialize modules
images.init();
menu.init();
clicktracking.init();
triggeredEventTracking.init();
adReload.init();
saveGetToCookie.init();
zeit.clearQueue();

if ( article ) {
    comments.init();
    articledate.init();
}

// add required jQuery plugins
require( 'velocity.ui' );
require( 'web.core/plugins/jquery.scrollIntoView' ); // plugin used by other plugins
require( 'web.core/plugins/jquery.animatescroll' );
require( 'web.core/plugins/jquery.toggleRegions' );
require( 'web.core/plugins/jquery.infobox' );
require( 'web.core/plugins/jquery.inlinegallery' );
require( 'web.core/plugins/jquery.imageCopyrightFooter' );
require( 'web.core/plugins/jquery.countFormchars' );
require( 'web.core/plugins/jquery.notifications' );

$.notifications();
$( '.js-scroll' ).animateScroll();

switch ( pageType ) {
    case 'article':
        main.find( '.js-infobox' ).infobox();
        main.find( '.article-toc' ).toggleRegions();
        main.find( '.comment-section' ).countFormchars();
        visibilityTracking.init();

    /* falls through */
    case 'gallery':
        main.find( '.js-gallery' ).inlinegallery();
}

$( '.js-image-copyright-footer' ).imageCopyrightFooter();
