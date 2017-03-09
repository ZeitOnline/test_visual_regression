// jscs:disable requireCamelCaseOrUpperCaseIdentifiers
/**
 * @fileOverview Module for losely counting adblocker user (just trends; not excact counts)
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
define([ 'jquery' ], function( $ ) {

    /**
     * oldAdBlockTest
     * checks if the old adblocker honeypotdiv is blocked
     * @return {bool}
     */
    function oldAdBlockTest( $elem ) {
        return $elem.length > 0 && $elem.is( ':hidden' );
    }

    /**
     * adControllerBlocked
     * checks if the adcontroller is linked, but blocked by user
     * @return {bool}
     */
    function adControllerBlocked() {
        if ( $( 'head script[src*="iqadcontroller"]' ).length > 0 ) {
            return typeof window.AdController === 'undefined';
        }
        return false;
    }

    return {

        /**
         * Init
         * prepare Adblockertest and start them on load
         */
        init: function() {
            var track = {
                    event: 'dataLayerEvent',
                    dataLayerEventCategory: 'AdBlockerDetection',
                    dataLayerEventAction: false
                },
                debug = window.location.search.indexOf( 'ablocktestdebug' ) !== -1;

            $( window ).on( 'load', function() {
                var $elem = $( '#ad3999' );
                if ( $elem.length > 0 ) {
                    if ( oldAdBlockTest( $elem ) ) {
                        track.dataLayerEventAction = true;
                        track.dataLayerEventLabel = 'adblockdesktop';
                    } else if ( adControllerBlocked() ) {
                        track.dataLayerEventAction = true;
                        track.dataLayerEventLabel = 'adcontrollerblocked';
                    }
                    window.dataLayer = window.dataLayer || [];
                    window.dataLayer.push( track );
                    if ( debug ) {
                        console.debug( track );
                    }
                } else {
                    if ( debug ) {
                        console.info( 'Not AdBlockerDetection tracked, ads disabled.' );
                    }
                }
            });
        }
    };
});
