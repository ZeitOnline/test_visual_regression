var $ = require( 'jquery' ),
    zeit = require( 'web.core/zeit' ),
    images = require( 'web.core/images' ),
    clicktracking = require( 'web.core/clicktracking' ),
    triggeredEventTracking = require( 'web.core/triggeredEventTracking' ),
    visibilityTracking = require( 'web.core/visibilityTracking' ),
    adReload = require( 'web.core/adReload' ),
    menu = require( 'web.core/menu' ),
    saveGetToCookie = require( 'web.core/saveGetToCookie' ),
    videoPlayer = require( 'web.core/video/videoPlayer' ),
    articledate = require( 'web.core/articledate' ),
    comments = require( 'web.core/comments' ),
    dataProtectionPopOver = require( 'web.core/dataProtectionPopOver' ),
    main = $( '#main' ),
    article = $( '#js-article' ),
    pageType = document.body.getAttribute( 'data-page-type' );

// initialize modules
images.init();
menu.init();
clicktracking.init();
triggeredEventTracking.init();
adReload.init();
dataProtectionPopOver.init();

if ( article.length ) {
    articledate.init();
    comments.init();
    visibilityTracking.init();
    videoPlayer.init();
}

saveGetToCookie.init();
zeit.clearQueue();

// add required jQuery plugins
require( 'web.core/vendor/modernizr-custom' );
require( 'velocity.ui' );
require( 'web.core/plugins/jquery.notifications' );
require( 'web.core/plugins/jquery.imageCopyrightFooter' );
require( 'web.core/plugins/jquery.toggleRegions' );
require( 'web.core/plugins/jquery.dropdownLink' );
require( 'web.core/plugins/jquery.inlinegallery' );
require( 'web.core/plugins/jquery.infobox' );
require( 'web.core/plugins/jquery.countFormchars' );
require( 'web.core/plugins/jquery.animateJobs' );
require( 'web.core/plugins/jquery.toggleRegions' );
require( 'web.arbeit/plugins/jquery.shareBlocks' );

$.notifications();

if ( pageType === 'centerpage' ) {
    $( '.js-dropdownlink' ).dropdownLink();
} else if ( article.length ) {
    main.find( '.article-toc' ).toggleRegions();
    main.find( '.js-toggle-region' ).toggleRegions();
    main.find( '.js-gallery' ).inlinegallery();
    main.find( '.js-infobox' ).infobox();
    $( '.comment-section' ).countFormchars();
    main.find( '.js-shareblock' ).shareBlocks();
}

// more ("non critical") global stuff
$( '.js-image-copyright-footer' ).imageCopyrightFooter();
$( '.js-jobbox-animation' ).animateJobs();
