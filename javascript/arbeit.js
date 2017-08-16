var $ = require( 'jquery' ),
    images = require( 'web.core/images' ),
    clicktracking = require( 'web.core/clicktracking' ),
    menu = require( 'web.core/menu' ),
    main = $( '#main' ),
    article = $( '#js-article' ),
    comments = require( 'web.core/comments' ),
    pageType = document.body.getAttribute( 'data-page-type' );

// initialize modules
images.init();
menu.init();
clicktracking.init();

// add required jQuery plugins
require( 'web.core/plugins/jquery.notifications' );
require( 'web.core/plugins/jquery.imageCopyrightFooter' );
require( 'web.core/plugins/jquery.toggleRegions' );
require( 'web.core/plugins/jquery.dropdownLink' );
require( 'web.core/plugins/jquery.inlinegallery' );
require( 'web.core/plugins/jquery.infobox' );
require( 'web.core/plugins/jquery.countFormchars' );

$.notifications();

if ( article.length ) {
    comments.init();
    $( '.comment-section' ).countFormchars();
}

if ( pageType === 'centerpage' ) {
    $( '.js-dropdownlink' ).dropdownLink();
} else if ( article.length ) {
    main.find( '.article-toc' ).toggleRegions();
    main.find( '.js-gallery' ).inlinegallery();
    main.find( '.js-infobox' ).infobox();
}

$( '.js-image-copyright-footer' ).imageCopyrightFooter();
