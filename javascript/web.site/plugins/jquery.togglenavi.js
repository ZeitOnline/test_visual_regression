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
                var $menu = $( that ),
                    $menuLink = $menu.find( 'a' ),
                    $mainNav = $menu.closest( '.main_nav' );

                // toggle visibility of main navigation items
                $menuLink.on( 'click', function( event ) {
                    event.preventDefault();

                    $mainNav.toggleClass( 'main_nav--open' );
                    $menuLink.attr( 'aria-expanded', $mainNav.hasClass( 'main_nav--open' ) );
                });
            }
        };

        //run through search element and return object
        return this.each( function() {
            el.bindNaviEvents( this );
        });
    };
})( jQuery );
