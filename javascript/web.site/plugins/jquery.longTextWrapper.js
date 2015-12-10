/**
 * @fileOverview jQuery plugin to pimp storystream CPs
 * @author moritz.stoltenburg@zeit.de
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
(function( $ ) {
    function textWrapper( element, options ) {
        this.node = element;
        this.element = $( element );
        this.options = options;
        this.init();
    }

    textWrapper.prototype = {

        init: function() {
            this.wrapSiblings();
        },

        wrapSiblings: function() {
            var height = Math.ceil( this.element.height()),
                options = this.options,
                wrapper,
                container,
                firstChild;

            if ( height > options.minHeight ) {

                if ( options.wrap ) {
                    // either wrap element
                    wrapper = this.element.wrap(
                    '<div class="' + options.className + ' ' + options.className + '--wrapped"></div>' ).parent();
                } else {
                    // or use it directly
                    wrapper = this.element;
                    wrapper.addClass( options.className + '--wrapped' );
                }

                wrapper.on( 'click', function() {
                    $( this ).off( 'click' ).on( 'transitionend', function() {
                        this.className = options.classAfterClick;
                        this.removeAttribute( 'style' );
                    });
                    this.className = options.className;
                    this.style.maxHeight = ( height + 60 ) + 'px';
                });
            }
        }
    };

    $.fn.longTextWrapper = function( settings ) {

        // default is storystream
        var defaults = {
            className: 'storystream-markup-wrapper',
            classAfterClick: '',
            wrap: true,
            minHeight: 150
        },
        options = $.extend( {}, defaults, settings );

        return this.each( function() {
            new textWrapper( this, options );
        });
    };

})( jQuery );
