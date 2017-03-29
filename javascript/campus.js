
var $ = require( 'jquery' ),
    zeit = require( 'web.core/zeit' ),
    images = require( 'web.core/images' ),
    clicktracking = require( 'web.core/clicktracking' ),
    triggeredEventTracking = require( 'web.core/triggeredEventTracking' ),
    adReload = require( 'web.core/adReload' ),
    menu = require( 'web.core/menu' ),
    comments = require( 'web.core/comments' ),
    articledate = require( 'web.core/articledate' ),
    article = document.getElementById( 'js-article' ),
    pageType = document.body.getAttribute( 'data-page-type' ),
    main = $( '#main' );

// initialize modules
images.init();
menu.init();
clicktracking.init();
triggeredEventTracking.init();
adReload.init();
zeit.clearQueue();

if ( article ) {
    comments.init();
    articledate.init();
}

// add required jQuery plugins
import 'velocity.ui';
import 'web.core/plugins/jquery.scrollIntoView'; // plugin used by other plugins
import 'web.core/plugins/jquery.animatescroll';
import 'web.core/plugins/jquery.toggleRegions';
import 'web.core/plugins/jquery.infobox';
import 'web.core/plugins/jquery.inlinegallery';
import 'web.core/plugins/jquery.imageCopyrightFooter';
import 'web.core/plugins/jquery.referrerCount';
import 'web.core/plugins/jquery.countFormchars';
import 'web.core/plugins/jquery.notifications';

// remove jQuery from global scope (omit for external jQuery Plugins (e.g. Datenjornalismus))
if ( !zeit.queue.length ) {
    $.noConflict( true );
}

$( window ).referrerCount();
$.notifications();
$( '.js-scroll' ).animateScroll();

switch ( pageType ) {
    case 'article':
        main.find( '.js-infobox' ).infobox();
        main.find( '.article-toc' ).toggleRegions();
        main.find( '.comment-section' ).countFormchars();

    /* falls through */
    case 'gallery':
        main.find( '.js-gallery' ).inlinegallery();
}

$( '.js-image-copyright-footer' ).imageCopyrightFooter();
