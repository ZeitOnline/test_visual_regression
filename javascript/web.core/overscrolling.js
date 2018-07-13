/**
 * @fileOverview Script to overscroll content pages with a loaction switch to another page
 * @author nico.bruenjes@zeit.de
 * @version  0.2
 */
define([
    'jquery',
    'velocity.ui',
    'web.core/zeit',
    'web.core/clicktracking',
    'jquery.inview' ], function( $, Velocity, Zeit, Clicktracking ) {
    var defaults = {
            documentMinHeight: 800,
            jumpHash: '#overscroll-article',
            jumpTo: Zeit.actualHost + 'index' || 'http://www.zeit.de/index',
            livePreview: false,
            overscrollElement: '#overscrolling',
            previewAreaAdress: '/index/area/no-1',
            previewHeight: 600,
            previewOpacity: 0.4,
            previewPath: '/exampleimages/sitepreview/sitepreview.jpg',
            progressElement: '#circle_progress',
            progressElementBar: '#circle_progress_bar',
            progressText: 'Zurück zur Startseite',
            trackingBase: 'overscroll....',
            triggerElement: '.footer',
            scrollToTrigger: true
        },
        config,
        debug = location.href.indexOf( 'debug-overscrolling' ) !== -1;

    function isActive() {
        var isActivated = true,
            message,
            index,
            status = [{
                isActive: Zeit.overscrollingActive,
                message: 'active setting is off or missing'
            }, {
                isActive: $( document ).height() >= config.documentMinHeight,
                message: 'documentMinHeight not matched'
            }, {
                isActive: Zeit.breakpoint.get() === 'desktop',
                message: 'only on desktop'
            }, {
                isActive: Zeit.view.get( 'paywall' ) === '',
                message: 'paywall active'
            }, {
                isActive: $( 'body[data-overscrolling="off"]' ).length < 1,
                message: 'article deactivated from cms'
            }, {
                isActive: !Zeit.isWrapped,
                message: 'deactivated in app'
            }];

        for ( index = status.length; index--; ) {
            if ( !status[ index ].isActive ) {
                message = status[ index ].message;
                isActivated = false;
                break;
            }
        }

        if ( debug && !isActivated ) {
            console.debug( 'overscrolling: %s (overwritten by debug)', message );
            isActivated = true;
        }

        return isActivated;
    }

    function clickTrack( type ) {
        var data = [ config.trackingBase + type, config.jumpTo ];

        Clicktracking.send( data );
    }

    function animateCircle( $element, p ) {
        var r = $element.attr( 'r' ),
            c = Math.PI * ( r * 2 ),
            pct;
        if ( p > 100 ) {
            p = 100;
        } else if ( p < 0 ) {
            p = 0;
        }
        pct = ( ( 100 - p ) / 100 ) * c;
        $element.css({ strokeDashoffset: pct });
    }

    function animateCircleByScroll() {
        var windowBottom = $( window ).scrollTop() + $( window ).height(),
            elementOffset = $( config.overscrollElement ).offset().top,
            elementHeight = $( config.overscrollElement ).height(),
            partOfWay = parseInt( ( windowBottom - elementOffset )  * 100 / elementHeight ),
            $progressElement = $( config.progressElementBar ),
            indicatorOffset = $( config.overscrollElement ).offset().top + $( config.overscrollElement + '_indicator' ).height() + 25 + 25;
        if ( windowBottom >= elementOffset ) {
            animateCircle( $progressElement, partOfWay );
        } else {
            animateCircle( $progressElement, 0 );
        }
        if ( windowBottom > indicatorOffset ) {
            $( config.overscrollElement + '_indicator' ).addClass( 'overscrolling__indicator--fixed' );
        } else {
            $( config.overscrollElement + '_indicator' ).removeClass( 'overscrolling__indicator--fixed' );
        }
    }

    function loadElements() {
        // first untie the trigger event
        $( config.triggerElement ).off( 'inview' );
        // attach stuff
        var $template = $( '#circle_progress_script' ),
            $element = $( $template.html() ),
            $target = $element.find( config.overscrollElement + '_target' ),
            $indicator = $element.find( config.overscrollElement + '_indicator' );

        // add text
        $indicator.attr( 'data-text', config.progressText );
        // preview image case
        if ( !config.livePreview ) {
            var img = $( '<img alt="">' ).attr( 'src', config.previewPath );
            $target.css({
                height: config.previewHeight,
                opacity: config.previewOpacity,
                overflow: 'hidden'
            }).append( img );
            // insert the shite
            $element.insertBefore( $template );
        } else {
            // load first teaser on homepage
            $target.css({
                height: config.previewHeight,
                opacity: config.previewOpacity,
                overflow: 'hidden'
            }).addClass( 'overscrolling__target--with-header-image' );
            $element.insertBefore( $template );
            $target.load( config.previewAreaAdress, function() {
                var $noscript = $target.find( 'noscript[data-src]' ),
                    src = $noscript.attr( 'data-src' );
                if ( src ) {
                    $( '<img>' ).attr( 'src', src ).insertBefore( $noscript );
                }
                $target.find( 'a' )
                    .css({ cursor: 'default' })
                    .on( 'click', function( event ) {
                        event.preventDefault();
                    });
            });
        }

        $( config.overscrollElement ).on( 'inview', function( event, isInView ) {
            if ( isInView ) {
                $( config.overscrollElement ).off( 'inview' );
                clickTrack( 'appear' );
            }
        });

        // make indicator clickable
        $( config.overscrollElement + '_indicator' ).on( 'click', function( event ) {
            event.preventDefault();
            if ( debug ) {
                console.debug( 'overscrolling: click jump to HP.' );
            } else {
                clickTrack( 'clickToHP' );
                window.location.href = config.jumpTo; // click w/o hash
            }
        });

        $( window ).on( 'scroll.over', Zeit.throttle( function() {
            animateCircleByScroll();
            if ( $( window ).scrollTop() >= $( document ).height() - $( window ).height() ) {
                if ( debug ) {
                    console.debug( 'overscrolling: jump to HP.' );
                } else {
                    clickTrack( 'scrollToHP' );
                    if ( config.scrollToTrigger && history.pushState ) {
                        history.pushState( null, null, '#!top-of-overscroll' );
                    }
                    window.location.href = config.jumpTo + config.jumpHash;
                }
            }
        }, 25 ) );
    }

    return {
        init: function( options ) {
            config = $.extend( defaults, options );
            if ( !isActive() ) {
                return;
            }
            if ( window.location.href.indexOf( '#!top-of-overscroll' ) > -1  && history.pushState ) {
                if ( 'scrollRestoration' in history ) {
                    history.scrollRestoration = 'manual';
                    var scrollPos = $( config.triggerElement ).position().top - $( window ).height();
                    $( 'html' ).velocity( 'scroll', {
                        offset: scrollPos,
                        mobileHA: false,
                        complete: function() {
                            history.pushState( '', document.title, window.location.pathname + window.location.search );
                        }
                    });
                } else {
                    if ( debug ) {
                        console.debug( 'exiting to prevent reload hell' );
                    }
                    return;
                }
            }
            $( config.triggerElement ).on( 'inview', function( event, isInView ) {
                if ( isInView && Zeit.breakpoint.get() === 'desktop' ) {
                    loadElements();
                }
            });
        }
    };

});
