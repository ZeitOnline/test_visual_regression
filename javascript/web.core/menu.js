/**
 * @fileOverview Module for ZEIT Campus menu
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
define([ 'jquery', 'velocity.ui', 'web.core/zeit' ], function( $, Velocity, Zeit ) {

    var visibleSubmenu;

    function toggleElement( control, expand, duration ) {

        if ( duration === undefined ) {
            duration = 200;
        }

        var target = $( '#' + control.attr( 'aria-controls' ) ),
            isNavigation = target.attr( 'id' ) === 'navigation',
            animation = expand ? 'slideDown' : 'slideUp',
            options = {
                duration: ( isNavigation ) ? 300 : duration,
                display: ''
            };

        control.attr({
            'aria-expanded': expand
        });

        if ( expand && !isNavigation ) {
            if ( visibleSubmenu ) {
                toggleElement( visibleSubmenu, false, 0 );
            }
            visibleSubmenu = control;
        } else {
            visibleSubmenu = undefined;
        }

        if ( expand ) {
            target.attr( 'aria-hidden', !expand );
        } else {
            options.complete = function() {
                target.attr( 'aria-hidden', true );
            };
        }

        target.velocity( animation, options );
    }

    return {
        init: function() {
            var menu = $( 'header.header' );

            menu.on( 'click', '*[aria-controls]', function( event ) {
                var control = $( this ),
                    expanded = control.attr( 'aria-expanded' ) === 'true';

                // in mobile view we sometimes want to follow the link
                if ( !( Zeit.isMobileView() && control.data( 'follow-mobile' ) ) ) {
                    event.preventDefault();
                    toggleElement( control, !expanded );
                }

            });

            // toggle submenu "onFocusOut"
            menu.on( 'blur', '*[role="button"], *[aria-hidden] a', function( event ) {
                if ( visibleSubmenu ) {
                    setTimeout( function() {
                        var submenu = document.getElementById( visibleSubmenu.attr( 'aria-controls' ) ),
                            focused = visibleSubmenu.get( 0 ) === document.activeElement || $.contains( submenu, document.activeElement );

                        if ( !focused ) {
                            toggleElement( visibleSubmenu, false );
                        }
                    }, 1 );
                }
            });

            // Configure keyboard navigation
            menu.on( 'keydown', '*[role="button"]', function( event ) {
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
    };
});
