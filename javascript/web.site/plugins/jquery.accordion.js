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
            if ( !item.data( 'active' ) ) {
                this.hideItem( $( this.items ).not( item ) );
                this.showItem( item );
            }
        },

        showItem: function( item ) {
            item.data( 'active', true ).find( this.options.slide ).slideDown( this.options.duration );
        },

        hideItem: function( item ) {
            item.data( 'active', false ).find( this.options.slide ).slideUp( this.options.duration );
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
        var add,
            current;

        return this.each( function() {

            if ( !current ) {
                // very first item
                current = new Accordion( this, options );
            } else {
                add = $( this ).prev( current.options.wrapper ).length;

                if ( add ) {
                    current.addItem( this, true );
                } else {
                    current = new Accordion( this, options );
                }
            }
        });
    };

})( jQuery );
