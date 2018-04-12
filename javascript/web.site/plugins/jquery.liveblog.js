/**
 * @fileOverview jQuery plugin to pimp liveblog articles
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
( function( $, window, document ) {
    function Liveblog( element ) {
        this.node = element;
        this.element = $( element );

        this.init();
    }

    Liveblog.prototype = {

        init: function() {
            this.wrapSiblings();
        },

        uncoverSiblings: function( element ) {
            $( element ).on( 'transitionend', function() {
                this.className = '';
                this.removeAttribute( 'style' );
            });

            element.style.maxHeight = ( element.scrollHeight + 60 ) + 'px';
            element.className = 'liveblog-text-wrapper';
            element.blur();
            element.removeAttribute( 'role' );
            element.tabIndex = -1;
        },

        wrapSiblings: function() {
            var parent = this.element.parent(),
                height = Math.ceil( this.element.offset().top - parent.offset().top ),
                self = this,
                container,
                firstChild;

            if ( height > 150 ) {
                container = document.createElement( 'div' );
                container.className = 'liveblog-text-wrapper liveblog-text-wrapper--wrapped';
                container.setAttribute( 'role', 'button' );
                container.setAttribute( 'aria-label', 'Artikelinhalt anzeigen' );
                container.tabIndex = 0;

                while ( ( firstChild = this.node.parentNode.firstChild ) !== this.node ) {
                    container.appendChild( this.node.parentNode.removeChild( firstChild ) );
                }

                this.node.parentNode.insertBefore( container, this.node );

                $( container ).one( 'click', function() {
                    self.uncoverSiblings( this );
                }).one( 'keydown', function( event ) {
                    // do nothing if there are other special keys involved
                    if ( event.altKey || event.shiftKey || event.ctrlKey || event.metaKey ) {
                        return;
                    }

                    switch ( event.which ) {
                        case 13: // [RETURN]
                        case 32: // [SPACE]
                            self.uncoverSiblings( this );
                            break;
                    }
                });
            }
        }
    };

    $.fn.liveblog = function() {
        return this.each( function() {
            new Liveblog( this );
        });
    };

})( jQuery, window, document );
