var $ = require( 'jquery' ),
    images = require( 'web.core/images' ),
    menu = require( 'web.core/menu' ),
    main = $( '#main' );

// initialize modules
images.init();
menu.init();

// add required jQuery plugins
require( 'web.core/plugins/jquery.notifications' );
require( 'web.core/plugins/jquery.imageCopyrightFooter' );
require( 'web.core/plugins/jquery.toggleRegions' );

$.notifications();

main.find( '.article-toc' ).toggleRegions();
