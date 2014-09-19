/* global console */

/**
 * @fileOverview jQuery Plugin for toggling the Searchbox
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
    * Switches between hidden and viewable search input fiels
    * @class toggleSearch
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.toggleSearch = function() {

        var el = {
            bindSearchFormEvents: function( that ) {
                var $input = $( that ).find( '.search__input' ),
                    $buttonSearch = $( that ).find( '.search__button' ),
                    $buttonClose = $( that ).find( '.search__close' );

                //event for pressed search button
                $buttonSearch.on( 'click', function( event ) {
                    //only applies if input is hidden
                    if ( $input.is( ':hidden' ) ) {
                        event.preventDefault();
                        $input.show();
                        $buttonClose.show();
                        $buttonSearch.addClass( 'search__button--left-only' );
                    }
                });

                //event for pressed close button
                $buttonClose.on( 'click', function( event ) {
                    event.preventDefault();
                    $input.hide();
                    $buttonClose.hide();
                    $buttonSearch.removeClass( 'search__button--left-only' );
                    $buttonSearch.addClass( 'search__button--round' );
                });
            }
        };

        //run through data-video elements and return object
        return this.each( function() {
            el.bindSearchFormEvents( this );
        });
    };
})( jQuery );
