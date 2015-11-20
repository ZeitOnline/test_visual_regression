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
    'web.core/adReload',
    'web.core/overscrolling.js',
    'web.site/video/videoStage',
    'web.site/articledate',
    'web.site/articlesharing',
    'web.site/comments',
    'web.site/adblockCount.js'
], function( images, clicktracking, adReload, overscrolling, videoStage, articledate, articlesharing, comments, adblockCount ) {
    var article = document.getElementById( 'js-article' );
    images.init();
    clicktracking.init();
    adReload.init();
    videoStage.init();
    articledate.init();
    articlesharing.init();
    comments.init();
    adblockCount.init();
    if ( article ) {
        overscrolling.init();
    }
});

String.prototype.format = function() {
    var args = arguments;
    return this.replace( /{(\d+)}/g, function( match, number ) {
        return typeof args[number] !== 'undefined' ? args[number] : match ;
    });
};

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
    'web.site/plugins/jquery.animateJobs',
    'web.site/plugins/jquery.autoclick',
    'web.site/plugins/jquery.countFormchars',
    'web.site/plugins/jquery.extendfooter',
    'web.site/plugins/jquery.fixPosition',
    'web.site/plugins/jquery.hpOverlay',
    'web.site/plugins/jquery.imageCopyrightFooter',
    'web.site/plugins/jquery.infobox',
    'web.site/plugins/jquery.liveblog',
    'web.site/plugins/jquery.searchTools',
    'web.site/plugins/jquery.selectNav',
    'web.site/plugins/jquery.paginateTeasers',
    'web.site/plugins/jquery.snapshot',
    'web.site/plugins/jquery.storystream',
    'web.site/plugins/jquery.tabs',
    'web.site/plugins/jquery.togglenavi',
    'web.site/plugins/jquery.togglesearch',
    'web.site/plugins/jquery.updateSignals',
    'web.site/plugins/jquery.partnerDropdown'
], function( $, Velocity ) {
    var pageType = document.body.getAttribute( 'data-page-type' ),
        isHp = document.body.getAttribute( 'data-is-hp' ),
        article = $( '#js-article' );

    $( window ).referrerCount();
    // global and "above the fold"
    $( '.main_nav__search' ).toggleSearch();
    $( '.logo_bar__menu' ).toggleNavi();
    $( '.primary-nav' ).adaptToSpace();

    if ( pageType === 'centerpage' ) {
        // homepage
        if ( isHp === 'true' ) {
            $( '#snapshot' ).snapshot();
            $.hpOverlay();
        }
        // centerpage
        $.updateSignals();
        $( '#main' ).autoclick();
        $( '#series_select' ).selectNav();
        $( '.js-bar-teaser-paginate' ).paginateTeasers();
        $( '.js-accordion' ).accordion();
        $( '.storystream-markup__content--first' ).storystream();
        $( '.jobbox--animate' ).animateJobs();
        $( '.js-tabs' ).tabs();
        $( '.js-image-copyright-footer' ).imageCopyrightFooter();
        $( '.partner__action' ).boxDropdown();

    } else if ( article.length ) {
        // article, gallery etc.
        article.find( '.inline-gallery' ).inlinegallery({ slideSelector: '.slide' });
        article.find( '.js-infobox' ).infobox();
        article.find( '.liveblog' ).liveblog();
        $.picturefill();
        $( '.js-count-formchars' ).countFormchars();
        $( '.js-fix-position' ).fixPosition();
    }

    // more ("non critical") global stuff
    $( '.footer-publisher__more' ).extendFooter();
    $( '.js-scroll' ).animateScroll();
    // search
    $( '.search-form' ).searchTools();
});
