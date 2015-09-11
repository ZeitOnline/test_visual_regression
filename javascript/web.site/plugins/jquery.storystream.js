/**
 * @fileOverview jQuery plugin to pimp storystream CPs
 * @author moritz.stoltenburg@zeit.de
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
(function( $ ) {
    function Storystream( element ) {
        this.node = element;
        this.element = $( element );
        this.init();
    }

    Storystream.prototype = {

        init: function() {
            this.wrapSiblings();
        },

        wrapSiblings: function() {
            var height = Math.ceil( this.element.height()),
                wrapper,
                container,
                firstChild;

            if ( height > 150 ) {
                wrapper = this.element.wrap(
                    '<div class="storystream-markup-wrapper storystream-markup-wrapper--wrapped"></div>' ).parent();

                wrapper.on( 'click', function() {
                    $( this ).off( 'click' ).on( 'transitionend', function() {
                        this.className = '';
                        this.removeAttribute( 'style' );
                    });
                    this.className = 'storystream-markup-wrapper';
                    this.style.maxHeight = ( height + 60 ) + 'px';
                });
            }
        }
    };

    $.fn.storystream = function() {
        return this.each( function() {
            new Storystream( this );
        });
    };

})( jQuery );
