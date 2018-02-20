/**
 * @fileOverview jQuery Plugin to adapt the primary navigation to limited horizontal space
 * @author arne.seemann@zeit.de
 * @author anika.szuppa@zeit.de
 * @author moritz.stoltenburg@zeit.de
 * @version  0.2
 */
( function( $, Zeit ) {

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
            this.maxWidth = 0;
            this.node = element;
            this.element = $( element );
            this.featured = this.element.find( '.nav__ressorts-item--featured, .nav__ressorts-item--featured-dtag' );
            this.labeled = this.element.find( '.nav__ressorts-item--has-label' );
            this.secondary = this.element.find( '.nav__dropdown-item--has-label' );
            this.moreList = $( '#more-ressorts' );
            this.items = this.element.children()
                .not( '.nav__ressorts-item--has-dropdown' )
                .not( this.labeled )
                .not( this.featured );
            this.clonedItems = this.items.clone();
            this.clonedLabels = this.labeled.clone()
                .addClass( 'nav__dropdown-item--has-label' )
                .removeClass( 'nav__ressorts-item--has-label' );
            this.clonedSecondary = this.secondary.clone()
                .addClass( 'nav__ressorts-item--has-label' )
                .removeClass( 'nav__dropdown-item--has-label' );

            this.init();
        }

        Container.prototype = {
            init: function() {
                var self = this;

                // move advertorials to end of list
                this.element
                    .append( this.clonedSecondary )
                    .append( this.labeled );
                // copy all items to more list
                this.moreList
                    .append( this.clonedItems )
                    .append( this.clonedLabels );

                this.adapt();

                // trigger adaption on resize
                $( window ).on( 'resize', Zeit.debounce( function() {
                    self.adapt();
                }, 100 ) );
                // BUG-549
                // safari gets the width of pseudo elements wrong
                // found no better fix than measuring again late in process
                $( window ).on( 'load', function( event ) {
                    if ( self.isDesktop() && self.node.scrollWidth > self.maxWidth ||
                        self.items.filter( ':visible' ).length < ( self.items.length / 2 ) ) {
                        self.adapt();
                    }
                    $( this ).off( event );
                });
            },
            adapt: function() {
                var parent = this.element.parent();

                this.items.show();

                // do not adapt space on mobile
                if ( this.isDesktop() ) {
                    parent.removeClass( 'nav__ressorts--fitted' );
                    this.clonedItems.hide();
                    this.maxWidth = parent.width();

                    var index = this.items.length;

                    for ( ; index--; ) {
                        if ( this.node.scrollWidth > this.maxWidth ) {
                            this.items.eq( index ).hide();
                            this.clonedItems.eq( index ).show();
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
})( jQuery, window.Zeit );
