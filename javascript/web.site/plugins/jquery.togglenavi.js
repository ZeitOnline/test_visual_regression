/**
 * @fileOverview jQuery Plugin for toggling the mobile Navigation
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
    * @class toggleNavi
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.toggleNavi = function() {

        var el = {
            bindNaviEvents: function( that ) {
                var $buttonMenue = $( that ).find( 'a' ),
                    $toggleEls = $( '.main_nav' ).find( 'div[data-dropdown="true"]' ).add( '.beta-notice' ),
                    $icons = $buttonMenue.find( '.logo_bar__menue__image' ),
                    icons = [ 'icon-zon-logo-navigation_menu', 'icon-zon-logo-navigation_close' ];

                //toggle icon and visibility of dropdown elements
                $buttonMenue.on( 'click', function( event ) {
                    event.preventDefault();
                    if ( $buttonMenue.attr( 'aria-expanded' ) === 'false' ) {
                        $buttonMenue.attr( 'aria-expanded', 'true' );
                    } else if ( $buttonMenue.attr( 'aria-expanded' ) === 'true' ) {
                        $buttonMenue.attr( 'aria-expanded', 'false' );
                    }
                    $toggleEls.toggle();
                    $.each( icons, function( index, value ) {
                        $( $icons[0] ).toggleClass( value );
                        $( $icons[1] ).toggleClass( value + '-hover' );
                    });
                });
            }
        };

        //run through search element and return object
        return this.each( function() {
            el.bindNaviEvents( this );
        });
    };
})( jQuery );
