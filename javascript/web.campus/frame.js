
var $ = require( 'jquery' ),
    menu = require( 'web.core/menu' ),
    clicktracking = require( 'web.core/clicktracking' ),
    adReload = require( 'web.core/adReload' );

// initialize modules
menu.init();
clicktracking.init();
adReload.init();

// remove jQuery from global scope
$.noConflict( true );
