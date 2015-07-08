/**
 * @fileOverview Module an API for track events and clicks via webtrekk
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
define( [ 'jquery' ], function( $ ) {
    var track = function( $element ) {
            var type = 'text';
            if ( $element.attr( 'class' ).indexOf( 'button' ) !== -1 ) {
                type = 'button';
            } else if ( $element.closest( 'figure' ).length > 0 ) {
                type = 'image';
            }
            return [
                window.ZMO.breakpoint.value === 'desktop' ? 'stationaer' : window.ZMO.breakpoint.value, // breakpoint
                $element.closest( '.cp-region' ).index( '.main .cp-region' ) + 1, // region bzw. verortung
                $element.closest( '.cp-area' ).index() + 1, // area bzw. reihe
                $element.closest( 'article' ).index() + 1, // module bzw. spalte
                '', // subreihe
                type // bezeichner (image, button, text)
            ].join( '.' ) + '|' + $element.attr( 'href' ).replace( 'http://', '' ); // url
        },
        debug = document.location.href.indexOf( '?webtrekk-clicktacking-debug' ) > -1 || false;
    return {
        init: function() {
            if ( typeof window.ZMO === 'undefined' || typeof window.wt === 'undefined' ) {
                return;
            }
            var $links = $( '.main article a' ).not( '[data-wt-click]' );
            $links.on( 'click', function( event ) {
                if ( debug ) {
                    event.preventDefault();
                }
                var data = track( $( this ) );
                if ( debug ) {
                    console.debug( data );
                }
                if ( data ) {
                    window.wt.sendinfo({
                        linkId: data,
                        sendOnUnload: 1
                    });
                }
            });
        }
    };
});
