
var $ = require( 'jquery' ),
    zeit = require( 'web.core/zeit' ),
    menu = require( 'web.core/menu' ),
    clicktracking = require( 'web.core/clicktracking' ),
    adblockCount = require( 'web.site/adblockCount.js' ),
    adReload = require( 'web.core/adReload' );

// initialize modules
menu.init({ followMobile: 'always' });
clicktracking.init();
adblockCount.init();
adReload.init();
zeit.clearQueue();

// add required jQuery plugins
import 'web.core/plugins/jquery.scrollIntoView'; // plugin used by other plugins
import 'web.site/plugins/jquery.adaptnav';
import 'web.site/plugins/jquery.extendfooter';
import 'web.site/plugins/jquery.togglesearch';

// remove jQuery from global scope
$.noConflict( true );

// global and "above the fold"
$( '.nav__search' ).toggleSearch();
$( '.nav__ressorts-list' ).adaptToSpace();

// more ("non critical") global stuff
$( '.footer-publisher__more' ).extendFooter();
