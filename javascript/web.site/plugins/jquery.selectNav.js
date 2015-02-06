/* global console */

/**
 * @fileOverview jQuery Plugin for select navigation
 * @author nico.bruenjes@zeit.de
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
    * navigate to selected url from select form element
    * @class selectNav
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.selectNav = function() {

        //run through search element and return object
        return this.each( function() {
            $( this ).on( 'change', function(e) {
                e.preventDefault();
                var o = this.options, p = o[o.selectedIndex];
                window.location.replace('http://www.zeit.de/serie/' + $(p).data('url'), '_top');
            } );
        });
    };
})( jQuery );
