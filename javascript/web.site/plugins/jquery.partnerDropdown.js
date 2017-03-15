/**
 * @fileOverview jQuery Plugin for Dropdown in Partnerboxes
 * @author anika.szuppa@zeit.de
 * @version  0.1
 */
( function( $ ) {

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
    * handles dropdown in partner boxes
    * @class boxDropdown
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.boxDropdown = function() {

        function bindDropboxEvents( $element ) {
            var $dropdown = $element.find( '.partner__dropdown' ),
                $button = $element.find( '.partner__button-text' ),
                tracking = $dropdown.data( 'tracklink' );

            $dropdown.on( 'change', function() {
                var link = $dropdown.find( '.partner__dropdown-option:selected' ).attr( 'value' );
                if ( link ) {
                    $button.attr( 'href', link + tracking );
                }
            });
        }

        return this.each( function() {
            bindDropboxEvents( $( this ) );
        });
    };
})( jQuery );
