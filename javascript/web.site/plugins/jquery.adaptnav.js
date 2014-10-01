/* global console, debugger */

/**
 * @fileOverview jQuery Plugin to adapt the primary navigation to limited horizontal space
 * @author arne.seemann@zeit.de
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
    * @class adaptToSpace
    * @memberOf jQuery.fn
    */
    $.fn.adaptToSpace = function() {

        var el = {
            $nav: false,
            $feature: false,
            $items: false,
            $html: false,
            init: function( $that ) {

                //set globals
                this.$nav = $that;
                this.$feature = el.$nav.find( '.primary-nav__item--featured' );

                el.renderAdaptiveNav();

                //make adaption on resize possible too
                $( window ).on( 'resize', function() {
                    el.renderAdaptiveNav();
                });

            },
            isDesktop: function() {
                return ( $( '.logo_bar__menue, .main_nav' ).is( ':hidden' ) );
            },
            prepareHTML: function() {

                el.$html = $( '<li data-feature="dropdown" class="primary-nav__item">' +
                                '   <a class="primary-nav__link" href="#">mehr</a>' +
                                '   <ul class="primary-nav__list"></ul>' +
                                '</li>' );

                //reset nav if necessary
                el.$nav.find( 'li[data-feature="dropdown"]' ).remove();

                //set items
                el.$items = el.$nav.children( '.primary-nav__item' ).not( '.primary-nav__item--featured' );

            },
            getAvailableWidth: function() {
            //get size available in navi

                var featureWidth = el.$feature.outerWidth( true );
                return ( el.$nav.width() - featureWidth - 70 );

            },
            buildAppendList: function() {
            // compute which items need to be hidden and add to temporary dropdown-DOM

                //prepare fresh html to work with
                el.prepareHTML();

                var navWidth = 0,
                    threshold = el.getAvailableWidth(),
                    $appendList = el.$html.find( '.primary-nav__list' );

                //append items to new menue
                el.$items.each(function() {

                    navWidth += $( this ).outerWidth();
                    if ( navWidth > threshold ) {
                        $( this ).detach().appendTo( $appendList );
                    }

                });
            },
            appendListToDom: function() {
            // add temporary dropdown-DOM to the DOM, check for featured item

                var state = el.$feature ? el.$feature.before( el.$html ) : el.$nav.append( el.$html );

                //refresh items
                el.$items = el.$nav.children( '.primary-nav__item' );

                // after computation is done, show the glory
                el.$items.css( 'display', 'block' );

            },
            renderAdaptiveNav: function() {
                if ( el.isDesktop() && el.$nav ) {
                    el.buildAppendList();
                    el.appendListToDom();
                }
            }
        };

        //run through nav element and return object
        return this.each( function() {
            el.init( $(this) );
        });

    };
})( jQuery );
