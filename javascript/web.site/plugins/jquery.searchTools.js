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
            toggleOn: '.search-additional-queries__on',
            toggledElem: '.search-additional-queries__container',
            toggleOff: '.search-additional-queries__off',
            timeRange: '.search-timerange__legend',
            typeRange: '.search-typerange__legend'
        }, options ),
        toggleTarget = function( target ) {
            var className = target.substr( 1 );
            $( target ).toggleClass( className + '--hidden' );
        },
        toggleDropdown = function( target, self ) {
            var className = target.substr( 1 );
            $( target ).toggleClass( className + '--hidden' );
            if ( $( self ).hasClass( 'icon-dropdown-closed' ) ) {
                $( self ).removeClass( 'icon-dropdown-closed' );
                $( self ).addClass( 'icon-dropdown-opened' );
            } else {
                $( self ).removeClass( 'icon-dropdown-opened' );
                $( self ).addClass( 'icon-dropdown-closed' );
            }
        };

        return this.each( function() {

            $( defaults.toggleOn ).on( 'click', function( event ) {
                toggleTarget( defaults.toggleOn );
                toggleTarget( defaults.toggledElem );
            });

            $( defaults.toggleOff ).on( 'click', function( event ) {
                toggleTarget( defaults.toggledElem );
                toggleTarget( defaults.toggleOn );
            });

            $( defaults.timeRange ).on( 'click', function( event ) {
                toggleDropdown( '.search-timerange__extend', event.target );
            });

            $( defaults.typeRange ).on( 'click', function( event ) {
                toggleDropdown( '.search-typerange__extend', event.target );
            });

        });
    };
})( jQuery );
