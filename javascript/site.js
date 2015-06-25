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
    'web.site/plugins/jquery.togglesearch',
    'web.site/plugins/jquery.togglenavi',
    'web.site/plugins/jquery.adaptnav',
    'web.site/plugins/jquery.up2dateSignals',
    'web.site/plugins/jquery.extendfooter',
    'web.site/plugins/jquery.snapshot',
    'web.site/plugins/jquery.toggleBeta',
    'web.site/plugins/jquery.selectNav',
    'web.site/plugins/jquery.infobox',
    'web.site/plugins/jquery.liveblog',
    'web.site/plugins/jquery.searchTools'
], function( $ ) {
    $( window ).referrerCount();
    $( '.main_nav__search' ).toggleSearch();
    $( '.logo_bar__menue' ).toggleNavi();
    $( '.primary-nav' ).adaptToSpace();
    $( 'body[data-page-type=\'centerpage\']' ).up2dateSignals();
    $( '.footer-publisher__more' ).extendFooter();
    $( '.inline-gallery' ).inlinegallery({ slideSelector: '.slide' });
    $( '#snapshot' ).snapshot();
    $( '#beta-toggle' ).toggleBeta();
    $( '#series_select' ).selectNav();
    $( '.js-infobox' ).infobox();
    $( '#js-article' ).find( '.liveblog' ).liveblog();
    $( '.search-form' ).searchTools();
});
