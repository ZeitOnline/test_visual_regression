
var $ = require( 'jquery' ),
    zeit = require( 'web.core/zeit' ),
    images = require( 'web.core/images' ),
    clicktracking = require( 'web.core/clicktracking' ),
    triggeredEventTracking = require( 'web.core/triggeredEventTracking' ),
    visibilityTracking = require( 'web.core/visibilityTracking' ),
    adReload = require( 'web.core/adReload' ),
    menu = require( 'web.core/menu' ),
    videoPlayer = require( 'web.core/video/videoPlayer' ),
    articledate = require( 'web.core/articledate' ),
    comments = require( 'web.core/comments' ),
    cards = require( 'web.magazin/cards' ),
    photocluster = require( 'web.magazin/photocluster' ),
    saveGetToCookie = require( 'web.core/saveGetToCookie' ),
    dataProtectionPopOver = require( 'web.core/dataProtectionPopOver' ),
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
cards.init();
dataProtectionPopOver.init();

if ( article ) {
    articledate.init();
    comments.init();
    photocluster.init();
    visibilityTracking.init();
    videoPlayer.init();
}

saveGetToCookie.init();
zeit.clearQueue();

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
