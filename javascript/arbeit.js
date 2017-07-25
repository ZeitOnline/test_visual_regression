var $ = require( 'jquery' ),
    images = require( 'web.core/images' ),
    menu = require( 'web.core/menu' ),
    main = $( '#main' ),
    article = $( '#js-article' ),
    pageType = document.body.getAttribute( 'data-page-type' );

// initialize modules
images.init();
menu.init();

// add required jQuery plugins
require( 'web.core/plugins/jquery.notifications' );
require( 'web.core/plugins/jquery.imageCopyrightFooter' );
require( 'web.core/plugins/jquery.toggleRegions' );
require( 'web.core/plugins/jquery.dropdownLink' );

$.notifications();


if ( pageType === 'centerpage' ) {
    $( '.js-dropdownlink' ).dropdownLink();
} else if ( article.length ) {
    main.find( '.article-toc' ).toggleRegions();
}
