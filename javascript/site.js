var $ = require( 'jquery' ),
    zeit = require( 'web.core/zeit' ),
    images = require( 'web.core/images' ),
    clicktracking = require( 'web.core/clicktracking' ),
    triggeredEventTracking = require( 'web.core/triggeredEventTracking' ),
    adReload = require( 'web.core/adReload' ),
    menu = require( 'web.core/menu' ),
    overscrolling = require( 'web.core/overscrolling' ),
    videoStage = require( 'web.site/video/videoStage' ),
    articledate = require( 'web.core/articledate' ),
    comments = require( 'web.core/comments' ),
    adblockCount = require( 'web.site/adblockCount' ),
    article = $( '#js-article' ),
    pageType = document.body.getAttribute( 'data-page-type' ),
    isHp = document.body.getAttribute( 'data-is-hp' );

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
}

adblockCount.init();
zeit.clearQueue();

// add required jQuery plugins
import 'velocity.ui';
import 'web.core/plugins/jquery.scrollIntoView'; // plugin used by other plugins
import 'web.core/plugins/jquery.animatescroll';
import 'web.core/plugins/jquery.infobox';
import 'web.core/plugins/jquery.inlinegallery';
import 'web.core/plugins/jquery.picturefill';
import 'web.core/plugins/jquery.referrerCount';
import 'web.core/plugins/jquery.toggleRegions';
import 'web.core/plugins/jquery.countFormchars';
import 'web.core/plugins/jquery.imageCopyrightFooter';
import 'web.core/plugins/jquery.notifications';
import 'web.site/plugins/jquery.accordion';
import 'web.site/plugins/jquery.adaptnav';
import 'web.site/plugins/jquery.animateJobs';
import 'web.site/plugins/jquery.autoclick';
import 'web.site/plugins/jquery.extendfooter';
import 'web.site/plugins/jquery.fixPosition';
import 'web.site/plugins/jquery.hpOverlay';
import 'web.site/plugins/jquery.liveblog';
import 'web.site/plugins/jquery.searchTools';
import 'web.site/plugins/jquery.selectNav';
import 'web.site/plugins/jquery.paginateTeasers';
import 'web.site/plugins/jquery.longTextWrapper';
import 'web.site/plugins/jquery.truncateRegions';
import 'web.site/plugins/jquery.tabs';
import 'web.site/plugins/jquery.togglesearch';
import 'web.site/plugins/jquery.updateSignals';
import 'web.site/plugins/jquery.partnerDropdown';

// remove jQuery from global scope (omit for external jQuery Plugins (e.g. Datenjornalismus))
if ( !zeit.queue.length ) {
    $.noConflict( true );
}

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
