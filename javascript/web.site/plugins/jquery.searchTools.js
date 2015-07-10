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

    function toggleOptions() {
        $( this ).closest( '.search-options' )
            .toggleClass( 'search-options--open' )
            .find( '.search-range' ).removeClass( 'search-range--open' );
    }

    function toggleDropdown() {
        $( this ).parent()
            .toggleClass( 'search-range--open' )
            .siblings( '.search-range' ).removeClass( 'search-range--open' );
    }

    $.fn.searchTools = function() {
        return this.each( function() {
            $( this ).find( '.search-options__on, .search-options__off' ).on( 'click', toggleOptions );
            $( this ).find( '.search-range__legend' ).on( 'click', toggleDropdown );
        });
    };
})( jQuery );
