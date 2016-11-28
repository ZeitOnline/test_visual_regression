/**
 * @fileOverview zeit.web.site module
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
    'web.core/overscrolling.js',
    'web.site/video/videoStage',
    'web.core/articledate',
    'web.core/comments',
    'web.site/adblockCount.js'
], function(
    zeit,
    images,
    clicktracking,
    triggeredEventTracking,
    adReload,
    menu,
    overscrolling,
    videoStage,
    articledate,
    comments,
    adblockCount
) {
    var article = document.getElementById( 'js-article' );

    images.init();
    menu.init({ followMobile: 'always' });
    clicktracking.init();
    triggeredEventTracking.init();
    adReload.init();
    videoStage.init();

    if ( article ) {
        articledate.init();
        comments.init();
        //overscrolling.init();
        zeit.overscrolling = overscrolling;
    }

    adblockCount.init();
    zeit.clearQueue();
});

// add required jQuery plugins
// require jQuery first, so we don't have to shim simple plugins
// plugins that require other plugins or libraries must use the shim config
require([
    'jquery',
    'velocity.ui',
    'web.core/plugins/jquery.animatescroll',
    'web.core/plugins/jquery.infobox',
    'web.core/plugins/jquery.inlinegallery',
    'web.core/plugins/jquery.picturefill',
    'web.core/plugins/jquery.referrerCount',
    'web.core/plugins/jquery.scrollIntoView', // plugin used by other plugins
    'web.core/plugins/jquery.toggleRegions',
    'web.core/plugins/jquery.countFormchars',
    'web.core/plugins/jquery.imageCopyrightFooter',
    'web.core/plugins/jquery.notifications',
    'web.site/plugins/jquery.accordion',
    'web.site/plugins/jquery.adaptnav',
    'web.site/plugins/jquery.animateJobs',
    'web.site/plugins/jquery.autoclick',
    'web.site/plugins/jquery.extendfooter',
    'web.site/plugins/jquery.fixPosition',
    'web.site/plugins/jquery.hpOverlay',
    'web.site/plugins/jquery.liveblog',
    'web.site/plugins/jquery.searchTools',
    'web.site/plugins/jquery.selectNav',
    'web.site/plugins/jquery.paginateTeasers',
    'web.site/plugins/jquery.longTextWrapper',
    'web.site/plugins/jquery.truncateRegions',
    'web.site/plugins/jquery.tabs',
    'web.site/plugins/jquery.togglesearch',
    'web.site/plugins/jquery.updateSignals',
    'web.site/plugins/jquery.partnerDropdown'
], function( $, Velocity ) {
    var pageType = document.body.getAttribute( 'data-page-type' ),
        isHp = document.body.getAttribute( 'data-is-hp' ),
        article = $( '#js-article' );

    // remove jQuery from global scope
    $.noConflict( true );

    $( window ).referrerCount();
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
        $( '.jobbox--animate' ).animateJobs();
        $( '.js-tabs' ).tabs();
        $( '.partner__action' ).boxDropdown();
        $( '.js-truncate-region' ).truncateRegions();

    } else if ( article.length ) {
        // article, gallery etc.
        article.find( '.js-gallery' ).inlinegallery();
        article.find( '.js-infobox' ).infobox();
        article.find( '.liveblog' ).liveblog();
        article.find( '.article-toc' ).toggleRegions();
        $.picturefill();
        $( '.sharing-menu' ).toggleRegions();
        $( '.comment-section' ).countFormchars();
        $( '.js-fix-position' ).fixPosition();
    } else if ( pageType === 'author' ) {
        $( '.author-questions' ).longTextWrapper();
    }

    // more ("non critical") global stuff
    $( '.footer-publisher__more' ).extendFooter();
    $( '.js-scroll' ).animateScroll();
    $( '.js-image-copyright-footer' ).imageCopyrightFooter();
    // search
    $( '.search-form' ).searchTools();
});
