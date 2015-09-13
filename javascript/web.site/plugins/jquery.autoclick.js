/**
 * @fileOverview jQuery plugin to click article teaser on touch
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
(function( $, Modernizr ) {
    function autoclick( event ) {
        var insideLink = $( event.target ).closest( 'a' ).length,
            firstLink = $( this ).find( 'a' ).first();

        if ( insideLink ) {
            return true;
        }

        if ( firstLink ) {
            event.preventDefault();
            event.stopPropagation();

            firstLink.get( 0 ).click();
        }
    }

    $.fn.autoclick = function() {
        return this.each( function() {
            var hasTouch = Modernizr.touchevents || location.search === '?touch';

            if ( hasTouch ) {
                $( this ).on( 'click', 'article[data-unique-id]', autoclick );
            }
        });
    };

})( jQuery, window.Modernizr );
