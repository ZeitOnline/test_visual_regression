/**
 * @fileOverview Module and API for track events and clicks via webtrekk
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
/* -----------------------------------------------------------------------------

HOW DOES IT WORK?

Any Script or Plugin can send information to be tracked. Even inside of iframes
and cross-origin. It works via window.postMessage.

    var messageData = {
        'name': 'zonTriggeredEventTracking',
        'sender': 'videojs',
        'event': 'playerStarted',
        'videotitle': 'Send anything you want',
        'duration': 1200
    };
    window.parent.postMessage( JSON.stringify( messageData ), '*' );

To be exact: posting a message is not directed to this script. It is rather
broadcasted, and any script can listen to all the messages being broadcasted
by any other script. That's why there is some effort of filterig the desired
messages (see below).

To be recognized by this script, a posted message must meet these requirements:
- data must be a JSON string, containing
  - 'name': 'zonTriggeredEventTracking'
  - 'sender': 'myModule' // name of the script/plugin which broadcasted the message

Any other data inside the JSON is a "private thing" between the sending module
and the tracking function which needs to be defined here.

In the first version of this script (Nov 2015), there is no generic function
which maps input (JSON) directly to output (tracking).

What does this script do?

// _functions.dispatch.dispatchAllMessages
1) It listens to every(!) message which is received by the current window.
2) Everthing which is not a JSON string is ignored.
3) Everything which has no `data.name == 'zonTriggeredEventTracking'` is ignored.

// _functions.dispatch.dispatchTrackingMessages
4) The `data.sender` is analyzed and any known sender matched to a function inside this script.

// _functions.handleSpecificPlugin.trackVideojsEvent
5) For this specific sender, the data object can be analyzed and tracking can be triggered.

// _functions.sendTracking.sendVideoViewToIVW
6) Additionally, we have specific functions which handle tracking to a specific
   tracking tool. Currently, webtrekk and IVW are used, and both only for video
   tracking. This could be generalized in the future, if/as needed.

----------------------------------------------------------------------------- */
define([ 'jquery', 'web.core/clicktracking' ], function( $, Clicktracking ) {

    var EXPECTED_NAME = 'zonTriggeredEventTracking',
        debugMode = document.location.hash.indexOf( 'debug-clicktracking' ) > -1,

        // encapsulate the functions into groups to make the code more readable (hopefully)
        _functions = {
            sendTracking: {},
            handleSpecificPlugin: {},
            dispatch: {}
        },
        init;

    /* -------------------------------------------------------------------------
    Tracking functions which trigger the actual tracking
    ------------------------------------------------------------------------- */
    _functions.sendTracking.sendDataToWebrekk = function( data ) {
        if ( debugMode ) {
            var trackingData = Clicktracking.string( data );
            console.log( '[zonTriggeredEventTracking] Webtrekk data sent: ' );
            console.log( trackingData );
            window.trackingData = trackingData;
        } else {
            Clicktracking.send( data );
        }
    };

    _functions.sendTracking.sendVideoEventToWebtrekk = function( eventString ) {
        var $container,
            videoSize = '',
            videoSeries = '',
            videoProvider = '',
            videoPageUrl = window.location.host + window.location.pathname,
            data,
            videoData;

        // we blindly assume that there is only one player on the page. ...
        // If in the future we have multiple video players, the ID would need
        // to be sent inside the postMessage. That way we could find the video.
        $container = $( '.video-player' ).closest( 'article, figure[data-video-provider]' );

        if ( $container.length ) {
            videoData = $container.data();
            videoSize = videoData.videoSize;
            videoSeries = videoData.videoSeries;
            videoProvider = videoData.videoProvider;
            videoPageUrl = videoData.videoPageUrl || window.location.host + window.location.pathname;
        }

        data = [
            'video',
            videoSize,
            videoSeries,
            videoProvider,
            eventString,
            videoPageUrl
        ];

        _functions.sendTracking.sendDataToWebrekk( data );
    };

    _functions.sendTracking.sendVideoViewToIVW = function() {

        // we expect the ivw function to be on the page
        if ( typeof window.iom  === 'undefined' ||
             typeof window.iom.h !== 'function' ||
             typeof window.iam_data  === 'undefined' ) {
            return;
        }

        window.iam_data.cp = 'video';
        window.iom.h( window.iam_data, 1 );

        if ( debugMode ) {
            console.log( '[zonTriggeredEventTracking] IVW data sent: ' );
            console.log( window.iam_data );
        }
    };

    /* -------------------------------------------------------------------------
    Specific functions for plugins. Each one handles the data of one external plugin/module/script
    ------------------------------------------------------------------------- */
    _functions.handleSpecificPlugin.trackVideojsEvent = function( eventString ) {

        switch ( eventString ) {
            case 'playerStarted':
                _functions.sendTracking.sendVideoViewToIVW();
                _functions.sendTracking.sendVideoEventToWebtrekk( 'play' ); // eventString "play" defined by tracking team
                break;
            case 'contentStarted':
                _functions.sendTracking.sendVideoEventToWebtrekk( 'start' ); // eventString "start" defined by tracking team
                break;
            case 'contentCompleted':
                _functions.sendTracking.sendVideoEventToWebtrekk( 'complete' ); // eventString "complete" defined by tracking team
                break;
            case 'adStarted':
                _functions.sendTracking.sendVideoEventToWebtrekk( 'adstart' ); // eventString "adstart" defined by tracking team
                break;
        }

    };

    // we get nearly complete tracking slugs from meine.zeit.de
    _functions.handleSpecificPlugin.trackMeineZeitClickEvent = function( messageDataObject ) {
        // replace leading dot for current values in meine.zeit.de, may be removed soon
        var trackingData = messageDataObject.slug.replace( /^\./, '' ).split( '|' ),
            data = [
                trackingData[ 0 ],
                trackingData[ 1 ] // url
            ];

        _functions.sendTracking.sendDataToWebrekk( data );
    };

    /* -------------------------------------------------------------------------
    Dispatch functions: filter the incoming messages and match them to specific
    handlers.
    ------------------------------------------------------------------------- */

    _functions.dispatch.dispatchTrackingMessages = function( messageDataObject ) {

        if ( messageDataObject.sender === 'videojs' ) {
            _functions.handleSpecificPlugin.trackVideojsEvent( messageDataObject.event );
        }

        if ( messageDataObject.sender === 'meinezeit' ) {
            _functions.handleSpecificPlugin.trackMeineZeitClickEvent( messageDataObject );
        }

        if ( messageDataObject.sender === 'quiz' ) {
            // we get complete tracking data from quiz.zeit.de
            // no further specific plugin handling overhead is required
            _functions.sendTracking.sendDataToWebrekk( messageDataObject.data );
        }

    };

    _functions.dispatch.dispatchAllMessages = function( event ) {

        var messageDataObject;

        if ( typeof event.originalEvent === 'undefined' || typeof event.originalEvent.data !== 'string' ) {
            return;
        }

        // Avoid JSON-parsing of messages which are not JSON
        if ( event.originalEvent.data.indexOf( '{' ) !== 0 ) {
            return;
        }

        try {
            messageDataObject = JSON.parse( event.originalEvent.data );
        } catch ( e ) {
            return;
        }

        // filter every event which is irrelevant to this script.

        if ( typeof messageDataObject.name !== 'string' ||
            typeof messageDataObject.sender !== 'string' ) {
            return;
        }

        if ( messageDataObject.name !== EXPECTED_NAME ) {
            return;
        }

        // well. now we can handle the events.
        _functions.dispatch.dispatchTrackingMessages( messageDataObject );
        // ODER: $( window ).trigger( 'interaction.adreload.z', [ messageData.name, messageData.message ] );
        // ermöglichen, sobald es mal ohne postMessage von internem JS getriggert werden soll.

    };

    /* -------------------------------------------------------------------------
    Register the event handler for posted messages
    ------------------------------------------------------------------------- */
    init = function() {

        // make sure webtrekk is available
        if ( ( typeof window.wt === 'undefined' || typeof( window.wt.sendinfo ) !== 'function' ) && !debugMode ) {
            return;
        }

        $( window ).on( 'message', function( event ) {
            _functions.dispatch.dispatchAllMessages( event );
        });

    };

    return {
        init: init
    };
});
