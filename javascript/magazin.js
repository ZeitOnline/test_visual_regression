
var $ = require( 'jquery' ),
    zeit = require( 'web.core/zeit' ),
    images = require( 'web.core/images' ),
    clicktracking = require( 'web.core/clicktracking' ),
    triggeredEventTracking = require( 'web.core/triggeredEventTracking' ),
    visibilityTracking = require( 'web.core/visibilityTracking' ),
    adReload = require( 'web.core/adReload' ),
    menu = require( 'web.core/menu' ),
    comments = require( 'web.core/comments' ),
    errors = require( 'web.magazin/errors' ),
    cards = require( 'web.magazin/cards' ),
    photocluster = require( 'web.magazin/photocluster' ),
    saveGetToCookie = require( 'web.core/saveGetToCookie' ),
    pageType = document.body.getAttribute( 'data-page-type' ),
    article = document.getElementById( 'js-article' );

// remove jQuery from global scope (needles with node/webpack)
// $.noConflict( true );

// initialize modules
images.init();
menu.init();
clicktracking.init();
triggeredEventTracking.init();
adReload.init();
errors.init();
cards.init();
saveGetToCookie.init();
zeit.clearQueue();

if ( article ) {
    comments.init();
    photocluster.init();
    visibilityTracking.init();
}

// add required jQuery plugins
require( 'velocity.ui' );
require( 'web.core/plugins/jquery.scrollIntoView' ); // plugin used by other plugins
require( 'web.core/plugins/jquery.animatescroll' );
require( 'web.core/plugins/jquery.infobox' );
require( 'web.core/plugins/jquery.inlinegallery' );
require( 'web.core/plugins/jquery.picturefill' );
require( 'web.core/plugins/jquery.countFormchars' );
require( 'web.core/plugins/jquery.imageCopyrightFooter' );
require( 'web.core/plugins/jquery.notifications' );
require( 'web.magazin/plugins/jquery.backgroundvideo' );

if ( pageType === 'article' ) {
    $( '.js-infobox' ).infobox();
}

$.notifications();
$( '.js-gallery' ).inlinegallery();
$( 'div[data-backgroundvideo]' ).backgroundVideo();
$.picturefill();
$( 'main' ).animateScroll({ selector: '.js-scroll' });
$( '.comment-section' ).countFormchars();
$( '.js-image-copyright-footer' ).imageCopyrightFooter();
