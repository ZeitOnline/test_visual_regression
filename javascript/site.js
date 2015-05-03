/**
 * @fileOverview zeit.web.site module
 * @version  0.1
 */

// A hack for Modernizr and AMD.
// This lets Modernizr be in the <head> and also compatible with other modules.
define( 'modernizr', [], window.Modernizr );

// load config first including path and shim config
require([ 'config' ], function() {});

// required plain vanilla JS programs here
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

// add required jQuery-Plugins that are writte with AMD header here
// make a shim of them first
// plugins that require plugins need to make this requirement in the shim-section of config
require([
    'web.core/plugins/jquery.inlinegallery',
    'web.core/plugins/jquery.referrerCount',
    'web.site/plugins/jquery.togglesearch',
    'web.site/plugins/jquery.togglenavi',
    'web.site/plugins/jquery.adaptnav',
    'web.site/plugins/jquery.up2dateSignals',
    'web.site/plugins/jquery.scrollup',
    'web.site/plugins/jquery.extendfooter',
    'web.site/plugins/jquery.snapshot',
    'web.site/plugins/jquery.toggleBeta',
    'web.site/plugins/jquery.selectNav',
    'web.site/plugins/jquery.infobox',
    'web.site/plugins/jquery.searchTools'
], function() {
    $( window ).referrerCount();
    $( '.main_nav__search' ).toggleSearch();
    $( '.logo_bar__menue' ).toggleNavi();
    $( '.primary-nav' ).adaptToSpace();
    $( 'body[data-page-type=\'centerpage\']' ).up2dateSignals();
    $( '.footer-publisher__more' ).extendFooter();
    $( '.inline-gallery' ).inlinegallery({ slideSelector: '.slide' });
    $( '.snapshot' ).snapshot();
    $( '#beta-toggle' ).toggleBeta();
    $( '#series_select' ).selectNav();
    $( '.infobox' ).infobox();
    $( '.search-form' ).searchTools();
    // comment out till we decide if it should be used and how (as)
    // $( '.footer-links__button' ).scrollUp();
});
