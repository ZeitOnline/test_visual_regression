var $ = require( 'jquery' ),
    zeit = require( 'web.core/zeit' ),
    images = require( 'web.core/images' ),
    clicktracking = require( 'web.core/clicktracking' ),
    triggeredEventTracking = require( 'web.core/triggeredEventTracking' ),
    adReload = require( 'web.core/adReload' ),
    menu = require( 'web.core/menu' ),
    main = $( '#main' ),
    article = $( '#js-article' ),
    comments = require( 'web.core/comments' ),
    pageType = document.body.getAttribute( 'data-page-type' ),
    underlined = $( '[class$="--underlined"]' ),
    font = '';

// initialize modules
images.init();
menu.init();
clicktracking.init();
triggeredEventTracking.init();
adReload.init();
zeit.clearQueue();

// add required jQuery plugins
require( 'web.core/plugins/jquery.notifications' );
require( 'web.core/plugins/jquery.imageCopyrightFooter' );
require( 'web.core/plugins/jquery.toggleRegions' );
require( 'web.core/plugins/jquery.dropdownLink' );
require( 'web.core/plugins/jquery.inlinegallery' );
require( 'web.core/plugins/jquery.infobox' );
require( 'web.core/plugins/jquery.countFormchars' );
require( 'web.core/plugins/jquery.animateJobs' );
require( 'web.core/plugins/jquery.toggleRegions' );

$.notifications();

if ( pageType === 'centerpage' ) {
    $( '.js-dropdownlink' ).dropdownLink();
} else if ( article.length ) {
    main.find( '.article-toc' ).toggleRegions();
    main.find( '.js-toggle-region' ).toggleRegions();
    main.find( '.js-gallery' ).inlinegallery();
    main.find( '.js-infobox' ).infobox();
    comments.init();
    $( '.comment-section' ).countFormchars();
}

// more ("non critical") global stuff
$( '.js-image-copyright-footer' ).imageCopyrightFooter();
$( '.js-jobbox-animation' ).animateJobs();

// apply janky hack for foo yellow underline only if font PatronBold is present
// else apply text-decoration: underline as a more semantic and solid fallback
if ( underlined.length > 0 ) {
    font = window.getComputedStyle( underlined[ 0 ], null ).getPropertyValue( 'font-family' );
    if ( font.indexOf( 'PatronBold' ) > -1 ) {
        for ( var i = 0; i < underlined.length; i++ ) {
            underlined[ i ].className = underlined[ i ].className.replace( /\-\-underlined$/, '--underlined-skip' );
        }
    }
}
