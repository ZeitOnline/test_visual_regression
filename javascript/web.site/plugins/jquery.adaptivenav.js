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

        // only act if view is *not* mobile
        if ( $( '.main_nav > .logo_bar > .logo_bar__menue:hidden' ).size() > 0 ) {

            var $this = $(this),
                navigationContainerWidth = $this.width(),
                featuredItem = $this.children( '.primary-nav__item--featured' ).outerWidth(true),
                navWidthWIP = 0,
                threshold = navigationContainerWidth - featuredItem - 70,
                $dropdownMenuHTML = $( '<li data-feature="dropdown" class="primary-nav__item">' +
                    '   <a class="primary-nav__link" href="#">mehr</a>' +
                    '   <ul class="primary-nav__list">' +
                    '       <li class="primary-nav__item">me dropdown</li>' +
                    '   </ul>' +
                    '</li>' ),
                $appendableList = $dropdownMenuHTML.find( '.primary-nav__list' )[0],
                $allPrimaryNavItems = $this.children( '.primary-nav__item' ),
                $featuredNavItems = $this.children( '.primary-nav__item--featured' );

            console.log('[RESP-NAV]: width = ' + navigationContainerWidth + ' , threshold = ' + threshold);

            // compute which items need to be hidden and add to temporary dropdown-DOM
            $allPrimaryNavItems.not( '.primary-nav__item--featured' ).each(function() {
                var $this = $(this);
                navWidthWIP += $this.outerWidth();
                console.log($this.text() + ' – ' + $this.outerWidth() + ' / ' + navWidthWIP);

                if ( navWidthWIP > threshold ) {
                    $this.detach().appendTo( $appendableList );
                }
            });

            // add temporary dropdown-DOM to the DOM, check for featured item
            if ( $featuredNavItems.size() > 0 ) {
                $featuredNavItems.before( $dropdownMenuHTML );
            } else {
                $this.append( $dropdownMenuHTML );
            }
            $allPrimaryNavItems = $this.children( '.primary-nav__item' ); // refresh

            // after computation is done, show the glory
            $allPrimaryNavItems.css( 'display', 'block' );

            console.debug($this);
            console.debug( $dropdownMenuHTML[0].innerHTML );

            // $allPrimaryNavItems.hover( function(e) {
            //     $(this).toggleClass( '.primary-nav__item--active' ); //.children().show();
            //     // $(this).children('ul').show();
            // }, function() {
            //     $(this).stop().toggleClass( '.primary-nav__item--active' ); //.children('ul').hide();
            // });
        }
    };
})( jQuery );
