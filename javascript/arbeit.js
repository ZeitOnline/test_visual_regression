var $ = require( 'jquery' ),
    menu = require( 'web.core/menu' );

// initialize modules
menu.init();

// add required jQuery plugins
require( 'web.core/plugins/jquery.notifications' );
require( 'web.core/plugins/jquery.imageCopyrightFooter' );

$.notifications();
