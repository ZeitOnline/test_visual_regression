/**
 * @fileOverview Module for losely counting adblocker user (just trends; not excact counts)
 * @author nico.bruenjes@zeit.de
 * @version  0.2
 */
define( function() {

    /**
     * check if the adcontroller is included
     * @return {bool}
     */
    function adsActive() {
        return document.querySelectorAll( 'head script[src*="iqadcontroller"]' ).length > 0;
    }

    /**
     * the old trick of the block ad div
     * @return {bool}
     */
    function testAdblockDiv() {
        var elem = document.querySelector( '#ad3999' ) || [];
        return elem.length > 0 && elem.hidden;
    }

    /**
     * check if adcontroller is blocked from download
     * @return {bool}
     */
    function testAdcontroller() {
        return typeof window.AdController === 'undefined';
    }

    /**
     * logging helper - wraps if debug --> console.log
     * @return {void}
     */
    function log() {
        if ( window.location.search.indexOf( 'debug-adblocktest' ) !== -1 ) {
            console.log.apply( console, arguments );
        }
    }

    return {
        init: function() {
            log( 'adblocktest debug mode' );
            window.addEventListener( 'load', function() {
                var track = {
                    'event': 'dataLayerEvent',
                    'dataLayerEventCategory': 'AdBlockerDetection',
                    'dataLayerEventAction': 'not_detected',
                    'dataLayerEventLabel': undefined
                };
                if ( adsActive() ) {
                    if ( typeof window.gaData === 'undefined' ) {
                        // GA not present, we can't count anything
                        log( 'Google Analytics not present or suppressed.' );
                    }
                    if ( testAdcontroller() ) {
                        track.dataLayerEventAction = 'detected';
                        track.dataLayerEventLabel = 'adcontrollerblocked';
                        log( 'detected blocked adcontroller', track );
                    } else if ( testAdblockDiv() ) {
                        track.dataLayerEventAction = 'detected';
                        track.dataLayerEventLabel = 'adblockdesktop';
                        log( 'detected blocked element', track );
                    }
                    window.dataLayer = window.dataLayer || [];
                    window.dataLayer.push( track );
                } else {
                    log( 'No AdBlockerDetection tracked, ads disabled.' );
                }
            }, false );
        }
    };

});
