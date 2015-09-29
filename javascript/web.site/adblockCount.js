// jscs:disable requireCamelCaseOrUpperCaseIdentifiers
/**
 * @fileOverview Module for losely counting adblocker user (just trends not excact counts)
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
define([ 'jquery' ], function( $ ) {
    /**
     * Oldadblocktest
     * checks if the old adblocker honeypotdiv is blocked
     * @return {bool}
     */
    var oldadblocktest = function( $elem ) {
        return $elem.length > 0 && $elem.is( ':hidden' );
    },
    /**
     * Adcoltrollerblocked
     * checks if the adcontroller is linked but blocked by user
     * @return {bool}
     */
    adcontrollerblocked = function() {
        var $scripts = $( 'head script' ),
            value = false;
        $scripts.each( function() {
            if ( typeof $( this ).attr( 'src' ) !== 'undefined' && $( this ).attr( 'src' ).indexOf( 'iqadcontroller' ) > -1 ) {
                value = typeof window.AdController === 'undefined';
            }
        });
        return value;
    };
    return {
        /**
         * Init
         * prepare Adblockertest and start them on load
         */
        init: function() {
            var track = {
                category: 'adb',
                action: false
            },
            debug = window.location.search.indexOf( 'ablocktestdebug' );
            $( window ).on( 'load', function( evt ) {
                var $elem = $( '#ad3999' );
                if ( $elem.length > 0 ) {
                    if ( oldadblocktest( $elem ) ) {
                        track.action = true;
                        track.opt_label = 'adblockdesktop';
                    } else if ( adcontrollerblocked() ) {
                        track.action = true;
                        track.opt_label = 'adcontrollerblocked';
                    }
                } else {
                    if ( debug ) {
                        console.info( 'Not abb tracked, Ads disabled.' );
                    }
                }
                window.dataLayer = window.dataLayer || [];
                window.dataLayer.push( track );
                if ( debug ) {
                    console.debug( track );
                }
            });
        }
    };
});
