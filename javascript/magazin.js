
var $ = require( 'jquery' ),
    zeit = require( 'web.core/zeit' ),
    images = require( 'web.core/images' ),
    clicktracking = require( 'web.core/clicktracking' ),
    triggeredEventTracking = require( 'web.core/triggeredEventTracking' ),
    adReload = require( 'web.core/adReload' ),
    menu = require( 'web.core/menu' ),
    comments = require( 'web.core/comments' ),
    errors = require( 'web.magazin/errors' ),
    cards = require( 'web.magazin/cards' ),
    photocluster = require( 'web.magazin/photocluster' ),
    article = document.getElementById( 'js-article' );

// remove jQuery from global scope (needles with node/webpack)
// $.noConflict( true );

// initialize modules
images.init();
menu.init();
clicktracking.init();
triggeredEventTracking.init();
adReload.init();
errors.init();
cards.init();
zeit.clearQueue();

if ( article ) {
    comments.init();
    photocluster.init();
}

// add required jQuery plugins
import 'velocity.ui';
import 'web.core/plugins/jquery.scrollIntoView'; // plugin used by other plugins
import 'web.core/plugins/jquery.animatescroll';
import 'web.core/plugins/jquery.inlinegallery';
import 'web.core/plugins/jquery.picturefill';
import 'web.core/plugins/jquery.referrerCount';
import 'web.core/plugins/jquery.countFormchars';
import 'web.core/plugins/jquery.imageCopyrightFooter';
import 'web.core/plugins/jquery.notifications';
import 'web.magazin/plugins/jquery.backgroundvideo';

$( window ).referrerCount();
$.notifications();
$( '.js-gallery' ).inlinegallery();
$( 'div[data-backgroundvideo]' ).backgroundVideo();
$.picturefill();
$( 'main' ).animateScroll({ selector: '.js-scroll' });
$( '.comment-section' ).countFormchars();
$( '.js-image-copyright-footer' ).imageCopyrightFooter();
