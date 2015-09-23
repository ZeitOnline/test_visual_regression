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
    'web.core/images',
    'web.core/clicktracking',
    'web.site/video/videoStage',
    'web.site/articledate',
    'web.site/articlesharing',
    'web.site/comments'
], function( images, clicktracking, videoStage, articledate, articlesharing, comments ) {
    images.init();
    clicktracking.init();
    videoStage.init();
    articledate.init();
    articlesharing.init();
    comments.init();
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
    'web.site/plugins/jquery.accordion',
    'web.site/plugins/jquery.adaptnav',
    'web.site/plugins/jquery.autoclick',
    'web.site/plugins/jquery.extendfooter',
    'web.site/plugins/jquery.infobox',
    'web.site/plugins/jquery.liveblog',
    'web.site/plugins/jquery.storystream',
    'web.site/plugins/jquery.searchTools',
    'web.site/plugins/jquery.selectNav',
    'web.site/plugins/jquery.shuffleTeasers',
    'web.site/plugins/jquery.snapshot',
    'web.site/plugins/jquery.toggleBeta',
    'web.site/plugins/jquery.togglenavi',
    'web.site/plugins/jquery.togglesearch',
    'web.site/plugins/jquery.updateSignals',
    'web.site/plugins/jquery.countFormchars',
    'web.site/plugins/jquery.hpOverlay'
], function( $, Velocity ) {
    var pageType = document.body.getAttribute( 'data-page-type' ),
        article = $( '#js-article' );

    $( window ).referrerCount();
    // global and "above the fold"
    $( '.main_nav__search' ).toggleSearch();
    $( '.logo_bar__menu' ).toggleNavi();
    $( '.primary-nav' ).adaptToSpace();

    if ( pageType === 'centerpage' ) {
        // homepage
        $( '#snapshot' ).snapshot();
        $( '[data-is-hp="true"]' ).hpOverlay();
        // centerpage
        $.updateSignals();
        $( '#main' ).autoclick();
        $( '#series_select' ).selectNav();
        $( '.js-gallery-teaser-shuffle' ).shuffleTeasers();
        $( '.js-accordion' ).accordion();
        $( '.storystream-markup__content--first' ).storystream();
    } else if ( article.length ) {
        // article, gallery etc.
        article.find( '.inline-gallery' ).inlinegallery({ slideSelector: '.slide' });
        article.find( '.js-infobox' ).infobox();
        article.find( '.liveblog' ).liveblog();
        $.picturefill();
        $( '.js-count-formchars' ).countFormchars();
    }

    // more ("non critical") global stuff
    $( '.footer-publisher__more' ).extendFooter();
    $( '.js-scroll' ).animateScroll();
    // search
    $( '.search-form' ).searchTools();
    // beta
    $( '#beta-toggle' ).toggleBeta();
});
