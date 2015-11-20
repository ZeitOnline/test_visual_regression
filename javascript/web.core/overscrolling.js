/**
 * @fileOverview Script to overscroll content pages with a loaction switch to another page
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
define( [ 'jquery', 'jquery.throttle', 'jquery.inview' ], function( $ ) {
    var defaults = {
        jumpTo: 'http://www.zeit.de/#overscrolled',
        triggerElement: '.footer',
        livePreview: false,
        previewPath: 'http://localhost:9090/exampleimages/sitepreview/sitepreview.jpg',
        previewHeight: 550,
        previewOpacity: 0.4,
        progressElement: '#circle_progress',
        progressElementBar: '#circle_progress_bar',
        progressText: 'Zurück zur Startseite',
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
        $element.find( '#overscrolling_indicator' ).attr( 'data-text', config.progressText );
        // preview image case
        if ( !config.livepreview ) {
            var img = $( '<img alt="">' ).attr( 'src', config.previewPath );
            $element.find( '#overscrolling_target' )
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

        $( window ).on( 'scroll', $.throttle( function() {
            animateCircleByScroll();
            if ( $( window ).scrollTop() >= $( document ).height() - $( window ).height() ) {
                if ( debug ) {
                    console.debug( 'BÄMM!' );
                } else {
                    window.location.href = config.jumpTo;
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
            elementOffset = $( '#overscrolling' ).offset().top,
            elementHeight = $( '#overscrolling' ).height(),
            partOfWay = parseInt( ( windowBottom - elementOffset )  * 100 / elementHeight ),
            $progressElement = $( config.progressElementBar ),
            indicatorOffset = $( '#overscrolling' ).offset().top + $( '#overscrolling_indicator' ).height() + 25 + 25;
        if ( windowBottom >= elementOffset ) {
            animateCircle( $progressElement, partOfWay );
        } else {
            animateCircle( $progressElement, 0 );
        }
        if ( windowBottom > indicatorOffset ) {
            $( '#overscrolling_indicator' ).addClass( 'overscrolling__indicator--fixed' );
        } else {
            $( '#overscrolling_indicator' ).removeClass( 'overscrolling__indicator--fixed' );
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
                    }
                });
            }
        }
    };

});
