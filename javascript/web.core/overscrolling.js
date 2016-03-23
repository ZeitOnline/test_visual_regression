/**
 * @fileOverview Script to overscroll content pages with a loaction switch to another page
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
define( [
       'modernizr',
       'jquery',
       'velocity.ui',
       'web.core/zeit',
       'jquery.throttle',
       'jquery.inview' ], function( Modernizr, $, Velocity, Zeit ) {
    var defaults = {
        documentMinHeight: 800,
        jumpHash: '#overscroll-article',
        jumpTo: 'http://www.zeit.de/index',
        livePreview: false,
        overscrollElement: '#overscrolling',
        previewAreaAdress: '/index/area/no-1',
        previewHeight: 600,
        previewOpacity: 0.4,
        previewPath: '/exampleimages/sitepreview/sitepreview.jpg',
        progressElement: '#circle_progress',
        progressElementBar: '#circle_progress_bar',
        progressText: 'Zurück zur Startseite',
        trackingBase: 'stationaer.overscroll....',
        trackingSlugs: {
            view: 'appear',
            click: 'clickToHP',
            scroll: 'scrollToHP'
        },
        triggerElement: '.footer',
        scrollToTrigger: true
    },
    config,
    debug = location.search.indexOf( 'debug-overscrolling' ) !== -1,
    clickTrack = function( type, target ) {
        var trackingData = config.trackingBase + type + '|' + target;
        window.wt.sendinfo({
            linkId: trackingData,
            sendOnUnload: 1
        });
        $( window ).trigger( 'overscroll', { 'action': type } );
    },
    loadElements = function( options ) {
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
                })
                .append( img );
            // insert the shite
            $element.insertBefore( $template );
        } else {
            // load first teaser on homepage
            $target.css({
                    height: config.previewHeight,
                    opacity: config.previewOpacity,
                    overflow: 'hidden'
                })
                .addClass( 'overscrolling__target--with-header-image' );
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
                clickTrack( 'appear', config.jumpTo );
            }
        });

        // make indicator clickable
        $( config.overscrollElement + '_indicator' ).on( 'click', function( event ) {
            event.preventDefault();
            if ( debug ) {
                console.debug( 'overscrolling: click jump to HP.' );
            } else {
                clickTrack( 'clickToHP', config.jumpTo );
                window.location.href = config.jumpTo; // click w/o hash
            }
        });

        $( window ).on( 'scroll', $.throttle( function() {
            animateCircleByScroll();
            if ( $( window ).scrollTop() >= $( document ).height() - $( window ).height() ) {
                if ( debug ) {
                    console.debug( 'overscrolling: jump to HP.' );
                } else {
                    clickTrack( 'scrollToHP', config.jumpTo );
                    if ( config.scrollToTrigger && history.pushState ) {
                        history.pushState( null, null, '#!top-of-overscroll' );
                    }
                    window.location.href = config.jumpTo + config.jumpHash;
                }
            }
        }, 25 ));
    },
    animateCircle = function( $element, p ) {
        var r = $element.attr( 'r' ),
            c = Math.PI * ( r * 2 ),
            pct;
        if ( p > 100 ) { p = 100; }
        if ( p < 0 ) { p = 0; }
        pct = ( ( 100 - p ) / 100 ) * c;
        $element.css({ strokeDashoffset: pct });
    },
    animateCircleByScroll = function() {
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
    };

    return {
        init: function( options ) {
            if ( !Modernizr.svg ) {
                if ( debug ) { console.debug( 'overscrolling: no svg available' ); }
                return;
            }
            config = $.extend( defaults, options );
            if ( window.location.href.indexOf( '#!top-of-overscroll' ) > -1  && history.pushState ) {
                if ( 'scrollRestoration' in history ) {
                    history.scrollRestoration = 'manual';
                    var scrollPos = $( config.triggerElement ).position().top - $( window ).height();
                    $( 'html' ).velocity( 'scroll', { offset: scrollPos, mobileHA: false, complete: function() {
                        history.pushState( '', document.title, window.location.pathname + window.location.search );
                    } } );
                } else {
                    if ( debug ) { console.debug( 'exiting to prevent reload hell' ); }
                    return;
                }
            }
            if ( $( document ).height() >= config.documentMinHeight ) {
                // inview event to change to elemen
                $( config.triggerElement ).on( 'inview', function( event, isInView ) {
                    if ( isInView ) {
                        if ( Zeit.breakpoint.get() === 'desktop' ) {
                            // attach Elements
                            loadElements();
                        } else {
                            if ( debug ) { console.debug( 'overscrolling: not on desktop' ); }
                        }
                    }
                });
            } else {
                if ( debug ) { console.debug( 'overscrolling: documentMinHeight not matched' ); }
            }
        }
    };

});
