
var $ = require( 'jquery' ),
    zeit = require( 'web.core/zeit' ),
    menu = require( 'web.core/menu' ),
    clicktracking = require( 'web.core/clicktracking' ),
    adblockCount = require( 'web.site/adblockCount.js' ),
    adReload = require( 'web.core/adReload' ),
    framebuilderLoginStatus = require( 'web.core/framebuilderLoginStatus' );

// remove jQuery from global scope (needles with node/webpack)
// $.noConflict( true );

// initialize modules
framebuilderLoginStatus.init();
menu.init({ followMobile: 'always' });
clicktracking.init();
adblockCount.init();
adReload.init();
zeit.clearQueue();

// add required jQuery plugins
require( 'web.core/plugins/jquery.scrollIntoView' ); // plugin used by other plugins
require( 'web.site/plugins/jquery.adaptnav' );
require( 'web.site/plugins/jquery.extendfooter' );
require( 'web.site/plugins/jquery.togglesearch' );

// global and "above the fold"
$( '.nav__search' ).toggleSearch();
$( '.nav__ressorts-list' ).adaptToSpace();

// more ("non critical") global stuff
$( '.footer-publisher__more' ).extendFooter();
