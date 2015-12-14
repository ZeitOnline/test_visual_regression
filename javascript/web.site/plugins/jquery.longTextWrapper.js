/**
 * @fileOverview jQuery plugin to wrap long text
 * @author moritz.stoltenburg@zeit.de
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
(function( $ ) {
    function TextWrapper( element, options ) {
        this.node = element;
        this.element = $( element );
        this.options = options;
        this.init();
    }

    TextWrapper.prototype.init = function() {
        var height = Math.ceil( this.element.height()),
            className = this.node.className.split( /\s+/ ).shift() + '--wrapped',
            wrapper = this.element;

        if ( height > this.options.minHeight ) {
            wrapper.addClass( className );

            wrapper.on( 'click.wrap', function() {
                wrapper.off( 'click.wrap' ).on( 'transitionend', function() {
                    this.removeAttribute( 'style' );
                });
                wrapper.removeClass( className );
                this.style.maxHeight = ( height + 60 ) + 'px';
            });
        }
    };

    $.fn.longTextWrapper = function( settings ) {
        // default is storystream
        var defaults = {
                minHeight: 150
            },
            options = $.extend( {}, defaults, settings );

        return this.each( function() {
            new TextWrapper( this, options );
        });
    };

})( jQuery );
