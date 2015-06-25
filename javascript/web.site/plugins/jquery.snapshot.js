/**
* ZON Snapshot formally know as Bottompic Plugin
* snapshot picture is loaded after the part of the page is in the visible area
*
* Copyright (c) 2011-14 ZEIT ONLINE, http://www.zeit.de
* Dual licensed under the MIT and GPL licenses:
* http://www.opensource.org/licenses/mit-license.php
* http://www.gnu.org/licenses/gpl.html
*
* @author Nico Bruenjes
* @version 2.0
*
*/
(function( $ ) {

    $.fn.snapshot = function() {

        return this.each( function() {
            var shot = $( this );

            shot.parent().on( 'inview', function( event, isInView ) {
                // change html5 prop "hidden" (which is more accessible)
                shot.prop( 'hidden', false );
                shot.addClass( 'snapshot--visible' );

                // trigger browser reflow to enable the CSS transition
                // other solutions are
                // * window.getComputedStyle(element) [IE9+]
                // * window.setTimeout(function(){ ... }, 0)
                // * element.focus()
                // * element.offsetWidth = element.offsetWidth;
                shot.css( 'width' );

                shot.addClass( 'snapshot--uncovered' );
                $( this ).off( 'inview' );
            });
        });
    };

})( jQuery );
