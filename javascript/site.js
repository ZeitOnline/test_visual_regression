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
    'web.site/video/videoStage',
    'web.site/articledate',
    'web.site/articlesharing',
    'web.site/comments'
], function( images, videoStage, articledate, articlesharing, comments ) {
    images.init();
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
    'web.core/plugins/jquery.inlinegallery',
    'web.core/plugins/jquery.referrerCount',
    'web.site/plugins/jquery.adaptnav',
    'web.site/plugins/jquery.autoclick',
    'web.site/plugins/jquery.extendfooter',
    'web.site/plugins/jquery.infobox',
    'web.site/plugins/jquery.liveblog',
    'web.site/plugins/jquery.searchTools',
    'web.site/plugins/jquery.selectNav',
    'web.site/plugins/jquery.shuffleTeasers',
    'web.site/plugins/jquery.snapshot',
    'web.site/plugins/jquery.toggleBeta',
    'web.site/plugins/jquery.togglenavi',
    'web.site/plugins/jquery.togglesearch',
    'web.site/plugins/jquery.updateSignals'
], function( $ ) {
    var pageType = document.body.getAttribute( 'data-page-type' ),
        article = $( '#js-article' );

    $( window ).referrerCount();
    // global
    $( '.main_nav__search' ).toggleSearch();
    $( '.logo_bar__menu' ).toggleNavi();
    $( '.primary-nav' ).adaptToSpace();
    $( '.footer-publisher__more' ).extendFooter();

    if ( pageType === 'centerpage' ) {
        // homepage
        $( '#snapshot' ).snapshot();
        // centerpage
        $.updateSignals();
        $( '#main' ).autoclick();
        $( '#series_select' ).selectNav();
        $( '.js-gallery-teaser-shuffle' ).shuffleTeasers();
    } else if ( article.length ) {
        // article, gallery etc.
        article.find( '.inline-gallery' ).inlinegallery({ slideSelector: '.slide' });
        article.find( '.js-infobox' ).infobox();
        article.find( '.liveblog' ).liveblog();
    }

    // search
    $( '.search-form' ).searchTools();
    // beta
    $( '#beta-toggle' ).toggleBeta();
});
