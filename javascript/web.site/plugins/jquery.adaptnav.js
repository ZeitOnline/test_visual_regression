/**
 * @fileOverview jQuery Plugin to adapt the primary navigation to limited horizontal space
 * @author arne.seemann@zeit.de
 * @author anika.szuppa@zeit.de
 * @author moritz.stoltenburg@zeit.de
 * @version  0.2
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

        function Container( element ) {
            this.node = element;
            this.element = $( element );
            this.featured = this.element.find( '.nav__ressorts-item--featured' );
            this.labeled = this.element.find( '.nav__ressorts-item--has-label' );
            this.moreList = $( '#more-ressorts' );
            this.items = this.element.children()
                .not( '.nav__ressorts-item--has-dropdown' )
                .not( this.labeled )
                .not( this.featured );
            this.clones = this.items.clone();

            this.init();
        }

        Container.prototype = {
            init: function() {
                var self = this;

                // copy all items to more list
                this.moreList
                    .append( this.clones )
                    .append( this.labeled );

                this.adapt();

                // trigger adaption on resize
                $( window ).on( 'resize', $.debounce( function() {
                    self.adapt();
                }, 100 ));
            },
            adapt: function() {
                var parent = this.element.parent();

                this.items.show();

                // do not adapt space on mobile
                if ( this.isDesktop() ) {
                    parent.removeClass( 'nav__ressorts--fitted' );
                    this.clones.hide();

                    var maxWidth = parent.width(),
                        index;

                    for ( index = this.items.length; index--; ) {
                        if ( this.node.scrollWidth > maxWidth ) {
                            this.items.eq( index ).hide();
                            this.clones.eq( index ).show();
                        } else {
                            break;
                        }
                    }

                    parent.addClass( 'nav__ressorts--fitted' );
                }
            },
            isDesktop: function() {
                // check that some "desktop only" elements are visible
                return this.element.find( '.nav__ressorts-item--more' ).is( ':visible' );
            }
        };

        // run through collection and return object
        return this.each( function() {
            new Container( this );
        });

    };
})( jQuery );
