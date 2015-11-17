/**
 * @fileOverview jQuery Plugin to adapt the primary navigation to limited horizontal space
 * @author arne.seemann@zeit.de
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
     * Hides sections in the primary navigation and makes them accessible in the
     * dropdown of the "more"-section
     * @class adaptToSpace
     * @memberOf jQuery.fn
    */
    $.fn.adaptToSpace = function() {

        var el = {
            $nav: false,
            $feature: false,
            $items: false,
            $html: false,
            $moreList: false,
            $moreListItems: false,
            init: function( $that ) {

                //set globals
                this.$nav = $that;
                this.$items = el.$nav.children( '.primary-nav__item' ).
                    not( '*[data-id="more-dropdown"]' ).
                    not( '.primary-nav__item--featured' );
                this.$feature = el.$nav.find( '.primary-nav__item--featured' );

                this.$moreList = el.$nav.find( '.primary-nav__item[data-id="more-dropdown"]' );
                this.$moreListItems = el.$moreList.find( '.dropdown > .dropdown__item' );

                this.toggleNavItems();
                this.$nav.removeClass( 'primary-nav--js-no-overflow' );

                //make adaption on resize possible, too
                $( window ).on( 'resize', function() {
                    el.toggleNavItems();
                });
            },
            toggleNavItems: function() {

                // make sure to *not* fire on mobile
                if ( el.isDesktop() && el.$nav ) {
                    var navWidth = 0,
                        threshold = el.getAvailableWidth();

                    // shall the item be displayed?
                    el.$items.each(function() {
                        var $navItem = $( this ),
                            itemId = $navItem.data( 'id' ),
                            $dropdownItem = el.$moreListItems.filter( '[data-id="' + itemId + '"]' );

                        navWidth += $navItem.outerWidth();

                        if ( navWidth < threshold ) {
                            $navItem.show();
                            $dropdownItem.hide();
                        } else {
                            $navItem.hide();
                            $dropdownItem.show();
                        }
                    });
                } else {
                    // show all top sections on mobile
                    el.$items.show();
                }
            },
            isDesktop: function() {
                // check that some "mobile only"-divs aren't visible
                return ( $( '.main_nav .logo_bar__menu' ).is( ':hidden' ) );
            },
            getAvailableWidth: function() {
                //get size available in navi
                var featureWidth = el.$feature.outerWidth( true ),
                    moreWidth = el.$moreList.outerWidth( true ),
                    tolerance = el.$nav.outerWidth() * 0.01;
                return ( el.$nav.width() - featureWidth - moreWidth - tolerance );
            }
        };

        //run through nav element and return object
        return this.each( function() {
            el.init( $( this ) );
        });

    };
})( jQuery );
