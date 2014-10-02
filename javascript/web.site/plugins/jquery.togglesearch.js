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
                    $button = $( that ).find( '.search__button' );

                //event for pressed search button
                $button.on( 'click', function( event ) {
                    event.preventDefault();

                    if ( $input.is( ':hidden' ) ) {
                    //only applies if input is hidden
                        $input.addClass( 'search__input--visible' );
                        $button.addClass( 'search__button--right-only' );
                    } else if ( $input.hasClass( 'search__input--visible' ) && !$input.val() ){
                    //if input is empty we wanne hide it when search button is pressed again
                        return;
                    }

                    event.stopPropagation();
                });

                //event for pressed close button
                $( document ).on( 'click', function( event ) {
                    //test if element was already clicked open
                    if ( $input.hasClass( 'search__input--visible' ) ){
                        //test if click wasn't on input
                        if ( $( event.target ).attr( 'class' ) !== $input.attr( 'class' ) ){
                            $input.removeClass( 'search__input--visible' );
                            $button.removeClass( 'search__button--right-only' );
                            $button.addClass( 'search__button--round' );
                        }
                    }
                });

                //event to reset clickable state when resized
                $( window ).on( 'resize', function() {
                    $input.removeClass( 'search__input--visible' );
                    $button.removeClass( 'search__button--round' );
                    $button.removeClass( 'search__button--right-only' );
                });
            }
        };

        //run through search element and return object
        return this.each( function() {
            el.bindSearchFormEvents( this );
        });
    };
})( jQuery );
