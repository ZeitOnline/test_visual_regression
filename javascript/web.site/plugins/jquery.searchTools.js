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
            optionsHandle: '.search-options__on, .search-options__off',
            dropdownHandle: '.search-range__legend'
        }, options );

        function toggleOptions() {
            $( this ).closest( '.search-options' ).toggleClass( 'search-options--open' );
        }

        function toggleDropdown() {
            $( this ).parent().toggleClass( 'search-range--open' );
        }

        return this.each( function() {
            $( this ).find( defaults.optionsHandle ).on( 'click', toggleOptions );
            $( this ).find( defaults.dropdownHandle ).on( 'click', toggleDropdown );
        });
    };
})( jQuery );
