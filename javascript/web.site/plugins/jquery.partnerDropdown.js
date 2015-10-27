/**
 * @fileOverview jQuery Plugin for Dropdown in Partnerboxes
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
    * Switches between hidden and viewable mobile navigation
    * @class boxDropdown
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.boxDropdown = function() {

        var el = {
            bindDropboxEvents: function( that ) {

                var $dropdown = $( that ).find( '.pa-dropdown' ),
                    $button = $( that ).find( '.pa-button__text' ),
                    tracking = $dropdown.data( 'tracklink' );

                // toggle visibility of main navigation items
                $button.on( 'click', function( event ) {
                    var link = $dropdown.find( '.pa-dropdown__option:selected' ).attr( 'value' );
                    if ( link ) {
                        window.open( link + tracking, '_self' );
                    }
                });

            }
        };

        //run through search element and return object
        return this.each( function() {
            el.bindDropboxEvents( this );
        });
    };
})( jQuery );
