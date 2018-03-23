/**
 * @fileOverview accordion jQuery plugin
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
( function( $ ) {
    var defaults = {
        classname: 'buzz-accordion',
        duration: 300
    };

    function Accordion( element, options ) {
        this.tabs = [];
        this.parentNode = element.parentNode;

        this.options = $.extend({}, defaults, options );
        this.accordion = $( '<div/>' ).addClass( this.options.classname );

        this.init( element );
    }

    Accordion.prototype = {
        init: function( element ) {
            var self = this;

            this.accordion.insertBefore( element );
            this.addItem( element, true );

            // Configure click event handler
            this.accordion.on( 'click', '[aria-controls]', function( event ) {
                event.preventDefault();
                self.toggleItem( $( this ) );
            });

            // Configure keyboard navigation
            this.accordion.on( 'keydown', function( event ) {
                // do nothing if there are other special keys involved
                if ( event.altKey || event.shiftKey || event.ctrlKey || event.metaKey ) {
                    return;
                }

                // simple caching
                if ( !self.tabs.length ) {
                    self.tabs = self.accordion.find( '[aria-controls]' );
                }

                var index = self.tabs.index( document.activeElement ),
                    focus;

                if ( index !== -1 ) {
                    switch ( event.which ) {
                        case 35: // [END]
                            focus = self.tabs.length - 1;
                            break;

                        case 36: // [HOME]
                            focus = 0;
                            break;

                        case 37: // [LEFT]
                        case 38: // [UP]
                            focus = --index;
                            break;

                        case 39: // [RIGHT]
                        case 40: // [DOWN]
                            focus = ++index % self.tabs.length;
                            break;
                    }
                }

                if ( focus !== undefined ) {
                    event.preventDefault();
                    self.tabs.eq( focus ).focus();
                }
            });
        },

        toggleItem: function( tab ) {
            var expanded = tab.attr( 'aria-expanded' ) !== 'false';

            if ( !expanded ) {
                this.hideItem( this.accordion.find( '[aria-expanded="true"]' ) );
                this.showItem( tab );
            }
        },

        toggleTab: function( tab, expand, duration ) {
            var panel = $( '#' + tab.attr( 'aria-controls' ) ),
                animation = expand ? 'slideDown' : 'slideUp';

            tab.attr({
                'aria-disabled': expand,
                'aria-expanded': expand
            });

            panel
                .attr( 'aria-hidden', !expand )
                .velocity( animation, { duration: ( duration !== undefined ) ? duration : this.options.duration });
        },

        showItem: function( tab ) {
            this.toggleTab( tab, true );
        },

        hideItem: function( tab ) {
            this.toggleTab( tab, false );
        },

        addItem: function( element, expand ) {
            this.accordion.append( element );
            this.toggleTab( $( element ).find( '[aria-controls]' ), expand, 0 );
        }
    };

    $.fn.accordion = function( options ) {
        var current;

        return this.each( function() {

            // very first item or inside different area
            if ( !current || current.parentNode !== this.parentNode ) {
                current = new Accordion( this, options );
            } else {
                current.addItem( this, false );
            }
        });
    };

})( jQuery );
