/**
 * @fileOverview Script to overscroll content pages with a loaction switch to another page
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 * @todo load first article instead of image
 * @todo make navigation background image
 * @todo do not count on homepage, remove hash
 */
define( [ 'jquery', 'jquery.throttle', 'jquery.inview' ], function( $ ) {
    var defaults = {
        jumpHash: '#overscroll-artikel',
        jumpTo: 'http://www.zeit.de/',
        livePreview: false,
        overscrollElement: '#overscrolling',
        previewHeight: 550,
        previewOpacity: 0.4,
        previewPath: '/exampleimages/sitepreview/sitepreview.jpg',
        progressElement: '#circle_progress',
        progressElementBar: '#circle_progress_bar',
        progressText: 'Zurück zur Startseite',
        triggerElement: '.footer',
        windowMinHeight: 1000
    },
    config,
    debug = location.search.indexOf( 'debug-overscrolling' ) !== -1,
    loadElements = function( options ) {
        // first untie the trigger event
        $( config.triggerElement ).off( 'inview' );
        // attach stuff
        var $template = $( '#circle_progress_script' ),
            $element = $( $template.html() );

        // add text
        $element.find( config.overscrollElement + '_indicator' ).attr( 'data-text', config.progressText );
        // preview image case
        if ( !config.livepreview ) {
            var img = $( '<img alt="">' ).attr( 'src', config.previewPath );
            $element.find( config.overscrollElement + '_target' )
                .css({
                    height: config.previewHeight,
                    opacity: config.previewOpacity,
                    overflow: 'hidden'
                })
                .append( img );
        } else {
            // todo: add more element loading here
        }
        // insert the shite
        $element.insertBefore( $template );

        // make indicator clickable
        $( config.overscrollElement + '_indicator' ).on( 'click', function( event ) {
            event.preventDefault();
            if ( debug ) {
                console.debug( 'overscrolling: click jump to HP.' );
            } else {
                window.location.href = config.jumpTo; // click w/o hash
            }
        });

        $( window ).on( 'scroll', $.throttle( function() {
            animateCircleByScroll();
            if ( $( window ).scrollTop() >= $( document ).height() - $( window ).height() ) {
                if ( debug ) {
                    console.debug( 'overscrolling: jump to HP.' );
                } else {
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
            config = $.extend( defaults, options );
            if ( $( window ).height() >= config.windowMinHeight ) {
                // inview event to change to elemen
                $( config.triggerElement ).on( 'inview', function( isVisible ) {
                    if ( isVisible ) {
                        if ( typeof window.ZMO === 'object' && window.ZMO.breakpoint.get() === 'desktop' ) {
                            // attach Elements
                            loadElements();
                        }
                    } else {
                        if ( debug ) { console.debug( 'overscrolling: not on desktop' ); }
                    }
                });
            } else {
                if ( debug ) { console.debug( 'overscrolling: windowMinHeight not matched' ); }
            }
        }
    };

});
