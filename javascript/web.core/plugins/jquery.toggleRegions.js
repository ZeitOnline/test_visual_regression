/**
 * @fileOverview jQuery Plugin for expandable and collapsible regions using the WAI-ARIA aria-expanded state.
 *               WAI-ARIA aria-controls is used to maintain markup associations.
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
(function( $, Zeit ) {

    function toggleElement( control, target ) {
        var expand = control.attr( 'aria-expanded' ) !== 'true',
            animation = expand ? 'slideDown' : 'slideUp',
            options = {
                duration: 200,
                display: ''
            };

        control.attr( 'aria-expanded', expand );

        if ( expand ) {
            target.attr( 'aria-hidden', !expand );
        } else {
            options.complete = function() {
                target.attr( 'aria-hidden', true );
            };
        }

        target.velocity( animation, options );
    }

    function initRegion( element ) {

        var region = $( element ),
            controls = region.find( '[aria-controls]' ),
            breakpoint = Zeit.breakpoint.get();

        controls.each( function() {
            var control = $( this ),
                target = $( '#' + control.attr( 'aria-controls' ) ),
                expanded = control.attr( 'aria-expanded' ) === 'true',
                constrained = control.attr( 'data-constrained' ).split( /\s*,\s*/ );

            if ( constrained.length ) {
                // test viewport constraints
                if ( $.inArray( breakpoint, constrained ) === -1 ) {
                    return false;
                }
            }

            control.attr({
                'role': 'button',
                'aria-expanded': expanded,
                'tabindex': 0
            });

            target.attr({
                'role': 'region',
                'aria-labelledby': this.id,
                'aria-hidden': !expanded
            });

            // set click event
            control.on( 'click', function( event ) {
                if ( constrained.length ) {
                    breakpoint = Zeit.breakpoint.get();

                    // test viewport constraints
                    if ( $.inArray( breakpoint, constrained ) === -1 ) {
                        return false;
                    }
                }

                event.preventDefault();
                toggleElement( control, target );
            });
        });

        // Configure keyboard navigation
        region.on( 'keydown', '*[role="button"]', function( event ) {
            // do nothing if there are other special keys involved
            if ( event.altKey || event.shiftKey || event.ctrlKey || event.metaKey ) {
                return;
            }

            switch ( event.which ) {
                case 13: // [RETURN]
                case 32: // [SPACE]
                    event.preventDefault();
                    event.target.click();
                    break;
            }
        });
    }

    $.fn.toggleRegions = function() {
        return this.each( function() {
            initRegion( this );
        });
    };
})( jQuery, window.Zeit );
