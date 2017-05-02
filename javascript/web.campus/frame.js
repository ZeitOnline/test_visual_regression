
var menu = require( 'web.core/menu' ),
    clicktracking = require( 'web.core/clicktracking' ),
    adReload = require( 'web.core/adReload' );

// remove jQuery from global scope (needles with node/webpack)
// $.noConflict( true );

// initialize modules
menu.init();
clicktracking.init();
adReload.init();
