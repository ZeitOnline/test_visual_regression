/**
 * @fileOverview jQuery plugin to pimp liveblog articles
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
(function( $, window, document ) {
    function Liveblog( element ) {
        this.node = element;
        this.element = $( element );

        this.init();
    }

    Liveblog.prototype = {

        init: function() {
            this.wrapSiblings();
        },

        wrapSiblings: function() {
            var parent = this.element.parent(),
                height = Math.ceil( this.element.offset().top - parent.offset().top ),
                container,
                firstChild;

            if ( height > 150 ) {
                container = document.createElement( 'div' );
                container.className = 'liveblog-text-wrapper liveblog-text-wrapper--wrapped';

                while (( firstChild = this.node.parentNode.firstChild ) !== this.node ) {
                    container.appendChild( this.node.parentNode.removeChild( firstChild ) );
                }

                this.node.parentNode.insertBefore( container, this.node );

                $( container ).on( 'click', function() {
                    $( this ).off( 'click' ).on( 'transitionend', function() {
                        this.style.maxHeight = 'none';
                        this.style.overflow = 'visible';
                    });
                    this.className = 'liveblog-text-wrapper';
                    this.style.maxHeight = ( height + 60 ) + 'px';
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
