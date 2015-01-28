/* global console */

/**
 * @fileOverview jQuery Plugin for scrolling to top of site
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
    * Scroll to top of site
    * @class scrollUp
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.scrollUp = function() {

        //scroll to top of page
        function scrollToTop(){
            $( 'html, body' ).animate( { scrollTop: '0px' }, 100 );
        }

        //run through search element and return object
        return this.each( function() {
            $( this ).on( 'click', function(e) {
                e.preventDefault();
                scrollToTop();
            } );
        });
    };
})( jQuery );
