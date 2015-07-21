/**
 * @fileOverview Module an API for track events and clicks via webtrekk
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
define( [ 'jquery' ], function( $ ) {
    /**
     * trackElement - collection of the different functions to gather the needed info to track smth
     * @type {Object}
     */
    var trackElement = {
        /**
         * track elements in the main section
         * @param  {Object} $element jQuery Element with the link that was clicked
         * @return {string}          formatted linkId-string for webtrekk call
         */
        main: function( $element ) {
            var data = [], type = 'text';
            if ( $element.attr( 'class' ).indexOf( 'button' ) !== -1 ) {
                type = 'button';
            } else if ( $element.closest( 'figure' ).length > 0 ) {
                type = 'image';
            }
            data = [
                getBreakpoint(),
                $element.closest( '.cp-region' ).index( '.main .cp-region' ) + 1, // region bzw. verortung
                $element.closest( '.cp-area' ).index() + 1, // area bzw. reihe
                $element.closest( 'article' ).index() + 1, // module bzw. spalte
                '', // subreihe
                type, // bezeichner (image, button, text)
                $element.attr( 'href' ).replace( /http(s)?:\/\//, '' ) // url
            ];
            return formatTrackingData( data );
        },
        /**
         * track elements in the nav section section, i.e. links with data-id attribute that contains the complete webtrekk id
         * @param  {Object} $element jQuery Element with the link that was clicked
         * @return {string}          formatted linkId-string for webtrekk call
         */
        nav: function( $element ) {
            var data = [
                getBreakpoint(),
                $element.data( 'id' ),
                $element.attr( 'href' ).replace( /http(s)?:\/\//, '' ) // url
            ];
            return formatTrackingData( data );
        },
        /**
         * track links with data-id attribute that contains the complete webtrekk id
         * @param  {Object} $element jQuery Element with the link that was clicked
         * @return {string}          formatted linkId-string for webtrekk call
         */
        useDataId: function( $element ) {
            var data = [
                getBreakpoint(),
                $element.data( 'id' ),
                $element.attr( 'href' ).replace( /http(s)?:\/\//, '' ) // url
            ];
            return formatTrackingData( data );
        }
    },
    clickTrack = function( event ) {
        if ( event.data.debug ) {
            event.preventDefault();
        }
        var trackingData = trackElement[ event.data.funcName ]( $( event.target ).closest( 'a' ) );
        if ( event.data.debug ) {
            console.debug( trackingData );
        }
        if ( trackingData ) {
            window.wt.sendinfo({
                linkId: trackingData,
                sendOnUnload: 1
            });
        }
    },
    formatTrackingData = function( trackingData ) {
        var url = trackingData.pop();
        return trackingData.join( '.' ) + '|' + url;
    },
    /**
     * returns the current breakpoint, and replaces "desktop" with "stationaer"
     * @return {string}          breakpoint for webtrekk
     */
    getBreakpoint = function() {
        return window.ZMO.breakpoint.value === 'desktop' ? 'stationaer' : window.ZMO.breakpoint.value;
    };

    return {
        init: function() {
            if ( typeof window.ZMO === 'undefined' || typeof window.wt === 'undefined' ) {
                return;
            }
            /**
             * trackingLinks - a collection of jQuery-Objects to add trackElement to.
             * The keys represent the trackElement type, so add new types, or add to jQuery-Collection if type is already in use
             *
             * @type Object
             */
            var trackingLinks = {
                main: $( '.main article a' ).not( '[data-wt-click]' ),
                nav: $( '.main_nav a[data-id], .footer a[data-id]' ).not( '[data-wt-click]' ),
                useDataId: $( '.snapshot a[data-id]' ).not( '[data-wt-click]' )
            };
            // The key name is used for calling the corresponding function in this.tracking
            for ( var key in trackingLinks ) {
                if ( trackingLinks.hasOwnProperty( key ) ) {
                    trackingLinks[ key ].on( 'click', {
                        funcName: key,
                        debug: document.location.href.indexOf( '?webtrekk-clicktracking-debug' ) > -1 || false
                    }, clickTrack );
                }
            }
        }
    };
});
