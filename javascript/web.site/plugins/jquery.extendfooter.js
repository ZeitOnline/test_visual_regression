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

        //scroll to bottom
        function scrollToBottom() {
            var target = $( 'html,body' );
            target.animate( { scrollTop: target.height() }, 1000 );
        }

        //toggle footer display
        function toggleFooter( button ) {
            //done like this to get an inline block
            if ( $( '.footer-links__inner' ).is( ':visible' ) ) {
                toggleFooterText( button, 'Mehr' );
                $( '.footer-links__inner' ).slideToggle( 200 );
                $( '.footer-publisher__inner' ).not( '.footer-publisher__inner--isfirst' ).slideToggle( 200 );
                $( '.footer-links__seperator' ).css( 'display', 'none' );
            } else {
                toggleFooterText( button, 'Schließen' );
                $( '.footer-links__inner' ).css( 'display', 'inline-block' ).animate( { opacity: 1 }, 200 );
                $( '.footer-links__seperator' ).css( 'display', 'block' );
                $( '.footer-publisher__inner' ).css( 'display', 'inline-block' ).animate( { opacity: 1 }, 200 );
                scrollToBottom();
            }
        }

        //toggle footer text
        function toggleFooterText( button, text ) {
            $( button ).find( 'a' ).text( text );
        }

        //run through search element and return object
        return this.each( function() {
            $( this ).on( 'click', function(e) {
                e.preventDefault();
                toggleFooter( this );
            } );
        });
    };
})( jQuery );
