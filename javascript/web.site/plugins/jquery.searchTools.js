/* global GWPLine, GWPLine3, nsIqd_setBg */
/**
* ZON Search Tools
* adds funky functionality to otherwise obvious search features
*
* Copyright (c) 2011-14 ZEIT ONLINE, http://www.zeit.de
* Dual licensed under the MIT and GPL licenses:
* http://www.opensource.org/licenses/mit-license.php
* http://www.gnu.org/licenses/gpl.html
*
* @author Nico Bruenjes
* @version 1.0
*
*/
(function( $ ) {

    $.fn.searchTools = function( options ) {

        var defaults = $.extend({
            toggleOnClassName: 'search-additional-queries__on',
            toggledElemClassName: 'search-additional-queries__container',
            toggleOffClassName: 'search-additional-queries__off'
        }, options ),
        toggleTarget = function( target ) {
            $( target ).toggleClass( target + '--hidden' );
        };

        return this.each( function() {
            $( defaults.toggleOnClassName ).on( 'click', function( event ) {
                toggleTarget( defaults.toggleOnClassName );
                toggleTarget( defaults.toggledElemClassName );
            });

            $( defaults.toggleOffClassName ).on( 'click', function( event ) {
                toggleTarget( defaults.toggledElemClassName );
            });
        });
    };
})( jQuery );
