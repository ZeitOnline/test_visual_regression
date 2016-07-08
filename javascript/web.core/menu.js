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
        init: function( options ) {
            var menu = $( 'header.header' ),
                defaults = {
                    followMobile: 'default'
                },
                settings = $.extend( {}, defaults, options );

            menu.on( 'click', '*[aria-controls]', function( event, triggered ) {
                var control = $( this ),
                    expanded = control.attr( 'aria-expanded' ) === 'true',
                    followMobile = control.data( 'follow-mobile' );

                // in mobile view we sometimes want to follow the link
                if ( followMobile && Zeit.isMobileView() ) {
                    // if the event was only triggered by jQuery, raise a native event now
                    if ( triggered ) {
                        event.stopImmediatePropagation();
                        this.click();
                    }
                }
                // in desktop view we sometimes want to follow the link, too
                // but only if this is not a keyboard event
                else if ( followMobile && settings.followMobile === 'always' && !triggered ) {
                    // never follow anchor links
                    if ( this.hash && this.hash.charAt( 0 ) === '#' ) {
                        event.preventDefault();
                    }
                } else {
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
                        $( event.target ).trigger( 'click', true );
                        break;
                }
            });
        }
    };
});
