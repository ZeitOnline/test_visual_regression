/**
 * @fileOverview jQuery Plugin for extending footer
 * @author anika.szuppa@zeit.de
 * @version  0.1
 */
(function( $ ) {
    /**
    * See (http://jquery.com/)
    * @name jQuery
    * @alias $
    * @class jQuery Library
    * See the jQuery Library  (http://jquery.com/) for full details.  This just
    * documents the function and classes that are added to jQuery by this plug-in.
    */
    /**
    * See (http://jquery.com/)
    * @name fn
    * @class jQuery Library
    * See the jQuery Library  (http://jquery.com/) for full details.  This just
    * documents the function and classes that are added to jQuery by this plug-in.
    * @memberOf jQuery
    */
    /**
    * toggle view of footer areas for mobile devices
    * @class extendFooter
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.extendFooter = function() {
        var animationDuration = 300,
            scrollDuration = 500;

        // toggle footer display
        function toggleFooter( $button ) {
            var $slides = $button.nextAll( '.footer-publisher__row' ).add( '.footer-links__row' );

            $button.toggleClass( 'footer-publisher__more--expanded' );

            if ( $button.hasClass( 'footer-publisher__more--expanded' ) ) {
                $button.text( 'Schließen' ).velocity( 'scroll', scrollDuration );
                $slides.velocity( 'slideDown', { duration: animationDuration } );
            } else {
                $button.text( 'Mehr' );
                $slides.velocity( 'slideUp', { duration: animationDuration } );
            }
        }

        return this.each( function() {
            var $button = $( this );

            $button.on( 'click', function( e ) {
                e.preventDefault();
                toggleFooter( $button );
            } );
        });
    };
})( jQuery );
