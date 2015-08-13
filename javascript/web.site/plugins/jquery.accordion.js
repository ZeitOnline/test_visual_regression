/**
 * @fileOverview accordion jQuery plugin
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
(function( $ ) {
    var defaults = {
            wrapper: '.buzz-accordion',
            box: '.buzz-box',
            handle: '.buzz-box__heading',
            slide: '.buzz-box__teasers',
            duration: 300
        };

    function Accordion( element, options ) {
        this.items = [];
        this.parentNode = element.parentNode;

        this.options = $.extend( {}, defaults, options );
        this.wrapper = $( '<div/>' ).addClass( this.options.wrapper.slice( 1 ) );

        this.init( element );
    }

    Accordion.prototype = {
        init: function( element ) {
            var that = this;

            this.wrapper.insertBefore( element );

            this.wrapper.on( 'click', this.options.handle, function( event ) {
                var item = $( this ).closest( that.options.box );
                event.preventDefault();
                if ( this.blur ) { this.blur(); }
                that.toggleItem( item );
            });

            this.addItem( element );
        },

        toggleItem: function( item ) {
            if ( item.data( 'active' ) === false ) {
                this.hideItem( $( this.items ).not( item ) );
                this.showItem( item );
            }
        },

        showItem: function( item ) {
            item
                .data( 'active', true )
                .find( this.options.slide )
                .velocity( 'slideDown', { duration: this.options.duration } );
        },

        hideItem: function( item ) {
            item
                .data( 'active', false )
                .find( this.options.slide )
                .velocity( 'slideUp', { duration: this.options.duration } );
        },

        addItem: function( element, hide ) {
            this.wrapper.append( element );
            this.items.push( element );

            if ( hide ) {
                this.hideItem( $( element ) );
            }
        }
    };

    $.fn.accordion = function( options ) {
        var current;

        return this.each( function() {

            // very first item or inside different area
            if ( !current || current.parentNode !== this.parentNode ) {
                current = new Accordion( this, options );
            } else {
                current.addItem( this, true );
            }
        });
    };

})( jQuery );
