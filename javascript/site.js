var $ = require( 'jquery' ),
    zeit = require( 'web.core/zeit' ),
    images = require( 'web.core/images' ),
    clicktracking = require( 'web.core/clicktracking' ),
    triggeredEventTracking = require( 'web.core/triggeredEventTracking' ),
    visibilityTracking = require( 'web.core/visibilityTracking' ),
    adReload = require( 'web.core/adReload' ),
    menu = require( 'web.core/menu' ),
    overscrolling = require( 'web.core/overscrolling' ),
    videoStage = require( 'web.site/video/videoStage' ),
    videoPlayer = require( 'web.core/video/videoPlayer' ),
    articledate = require( 'web.core/articledate' ),
    comments = require( 'web.core/comments' ),
    adblockCount = require( 'web.site/adblockCount' ),
    saveGetToCookie = require( 'web.core/saveGetToCookie' ),
    article = $( '#js-article' ),
    pageType = document.body.getAttribute( 'data-page-type' ),
    isHp = document.body.getAttribute( 'data-is-hp' );

// remove jQuery from global scope (needles with node/webpack)
// $.noConflict( true );

// initialize modules
images.init();
menu.init({ followMobile: 'always' });
clicktracking.init();
triggeredEventTracking.init();
adReload.init();
videoStage.init();

if ( article.length ) {
    articledate.init();
    comments.init();
    overscrolling.init({ livePreview: true });
    visibilityTracking.init();
    videoPlayer.init();
}

adblockCount.init();
saveGetToCookie.init();
zeit.clearQueue();

// add required jQuery plugins
require( 'velocity.ui' );
require( 'web.core/plugins/jquery.scrollIntoView' ); // plugin used by other plugins
require( 'web.core/plugins/jquery.animatescroll' );
require( 'web.core/plugins/jquery.infobox' );
require( 'web.core/plugins/jquery.inlinegallery' );
require( 'web.core/plugins/jquery.picturefill' );
require( 'web.core/plugins/jquery.toggleRegions' );
require( 'web.core/plugins/jquery.countFormchars' );
require( 'web.core/plugins/jquery.imageCopyrightFooter' );
require( 'web.core/plugins/jquery.notifications' );
require( 'web.core/plugins/jquery.dropdownLink' );
require( 'web.site/plugins/jquery.accordion' );
require( 'web.site/plugins/jquery.adaptnav' );
require( 'web.core/plugins/jquery.animateJobs' );
require( 'web.site/plugins/jquery.autoclick' );
require( 'web.site/plugins/jquery.extendfooter' );
require( 'web.site/plugins/jquery.hpOverlay' );
require( 'web.site/plugins/jquery.liveblog' );
require( 'web.site/plugins/jquery.searchTools' );
require( 'web.site/plugins/jquery.selectNav' );
require( 'web.site/plugins/jquery.paginateTeasers' );
require( 'web.site/plugins/jquery.longTextWrapper' );
require( 'web.site/plugins/jquery.truncateRegions' );
require( 'web.site/plugins/jquery.tabs' );
require( 'web.site/plugins/jquery.togglesearch' );
require( 'web.site/plugins/jquery.updateSignals' );

// global and "above the fold"
$( '.nav__search' ).toggleSearch();
$( '.nav__ressorts-list' ).adaptToSpace();
$.notifications();

if ( pageType === 'centerpage' ) {
    // homepage
    if ( isHp === 'true' ) {
        $.hpOverlay();
    }
    // centerpage
    $.updateSignals();
    $( '#main' ).autoclick();
    $( '#series_select' ).selectNav();
    $( '.js-bar-teaser-paginate' ).paginateTeasers();
    $( '.js-accordion' ).accordion();
    $( '.storystream-markup__content--first' ).longTextWrapper();
    $( '.js-jobbox-animation' ).animateJobs();
    $( '.js-tabs' ).tabs();
    $( '.js-dropdownlink' ).dropdownLink();
    $( '.js-truncate-region' ).truncateRegions();
    $( '.js-toggle-region' ).toggleRegions();

} else if ( article.length ) {
    // article, gallery etc.
    article.find( '.js-gallery' ).inlinegallery();
    article.find( '.js-infobox' ).infobox();
    article.find( '.js-liveblog' ).liveblog();
    article.find( '.article-toc' ).toggleRegions();
    $.picturefill();
    $( '.sharing-menu' ).toggleRegions();
    $( '.comment-section' ).countFormchars();
} else if ( pageType === 'author' ) {
    $( '.author-questions' ).longTextWrapper();
}

// more ("non critical") global stuff
$( '.footer-publisher__more' ).extendFooter();
$( '.js-scroll' ).animateScroll();
$( '.js-image-copyright-footer' ).imageCopyrightFooter();

// search
$( '.search-form' ).searchTools();
