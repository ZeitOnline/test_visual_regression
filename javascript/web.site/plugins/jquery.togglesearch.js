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

                function resetInput( e ) {
                    var searchClick = $( e.target ).closest( '.search__input' ).length;

                    // test if click wasn't on input
                    if ( !searchClick ) {
                        $input.removeClass( 'search__input--visible' );
                        $( document ).off( 'click', resetInput );
                    }
                }

                function showInput() {
                    $input.addClass( 'search__input--visible' );
                    $( document ).on( 'click', resetInput );
                }

                // event for pressed search button
                $button.on( 'click', function( event ) {

                    if ( $input.css( 'visibility' ) === 'hidden' ) {
                        // only applies if input is hidden
                        event.preventDefault();
                        showInput();
                    } else if ( $input.hasClass( 'search__input--visible' ) && !$input.val() ) {
                        // if input is empty we wanne hide it when search button is pressed again
                        event.preventDefault();
                        return;
                    }

                    event.stopPropagation();
                });

                // event to reset clickable state when resized
                $( window ).on( 'resize', $.debounce( resetInput, 300 ) );
            }
        };

        // run through search element and return object
        return this.each( function() {
            el.bindSearchFormEvents( this );
        });
    };
})( jQuery );
