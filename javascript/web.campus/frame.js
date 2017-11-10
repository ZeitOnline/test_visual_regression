
var menu = require( 'web.core/menu' ),
    clicktracking = require( 'web.core/clicktracking' ),
    adReload = require( 'web.core/adReload' ),
    framebuilderLoginStatus = require( 'web.core/framebuilderLoginStatus' );

// remove jQuery from global scope (needles with node/webpack)
// $.noConflict( true );

// initialize modules
framebuilderLoginStatus.init();
menu.init();
clicktracking.init();
adReload.init();
