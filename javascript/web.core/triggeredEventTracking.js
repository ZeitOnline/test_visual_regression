// jscs:disable requireCamelCaseOrUpperCaseIdentifiers
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
define( [ 'jquery', 'web.core/zeit' ], function( $, Zeit ) {

    var EXPECTED_NAME = 'zonTriggeredEventTracking',
        debugMode,

        // encapsulate the functions into groups to make the code more readable (hopefully)
        _functions = {
            helpers: {},
            sendTracking: {},
            handleSpecificPlugin: {},
            dispatch: {}
        },
        init;

    /* -------------------------------------------------------------------------
    Helper functions for transforming data
    ------------------------------------------------------------------------- */
    _functions.helpers.formatWebtrekkTrackingData = function( trackingData ) {
        var url = trackingData.pop(),
            slug = trackingData.join( '.' );

        if ( url ) {
            url = url.replace( /http(s)?:\/\//, '' );

            // For some links, we want to preserve the GET parameters.
            // Otherwise, remove them!
            if ( !/\.(social|studiumbox)\./.test( slug ) ) {
                url = url.split( '?' )[0];
            }
        }
        return slug + '|' + url;
    };

    /* -------------------------------------------------------------------------
    Tracking functions which trigger the actual tracking
    ------------------------------------------------------------------------- */
    _functions.sendTracking.sendVideoEventToWebtrekk = function( eventString ) {

        // make sure webtrekk is available
        if ( typeof( window.wt ) === 'undefined' || typeof( window.wt.sendinfo ) !== 'function' ) {
            return;
        }

        var messageData,
            messageSender,
            $videoArticle,
            videoSeries = '', // no series info here. simply send an empty string
            videoProvider = '',
            videoSize = '',
            data,
            trackingData;

        // we blindly assume that there is only one player on the page. ...
        // If in the future we have multiple video players, the ID would need
        // to be sent inside the postMessage. That way we could find the video.
        $videoArticle = $( '.video-player' );
        if ( $videoArticle.length > 0 ) {
            videoProvider = $videoArticle.data( 'video-provider' ) || '';
            videoSize = $videoArticle.data( 'video-size' ) || '';
        }

        data = [
            Zeit.breakpoint.getTrackingBreakpoint(),
            'video',
            videoSize,
            videoSeries,
            videoProvider,
            '', // origin (zdf/reuters)
            eventString,
            window.location.host + window.location.pathname
        ];

        trackingData = _functions.helpers.formatWebtrekkTrackingData( data );

        window.wt.sendinfo({
            linkId: trackingData,
            sendOnUnload: 1
        });

        if ( debugMode ) {
            console.log( '[zonTriggeredEventTracking] Webtrekk data sent: ' );
            console.log( trackingData );
        }
    };

    _functions.sendTracking.sendVideoViewToIVW = function() {

        // we expect the ivw function to be on the page
        if ( typeof window.iom  === 'undefined' || typeof window.iom.c !== 'function' ) {
            return;
        }

        var iam_data = {
                'st': '', // dynamicallly set mobile|desktop
                'cp': 'video',
                'sv': 'mo', // 'mo' für alle Konten
                'co': 'URL: ' + window.location.pathname
            };

        // in our Wrapper-Apps: always use the 'Angebotskennung' for the 'MEW' (mobile enabled website)
        if ( Zeit.isMobileView() || Zeit.is_wrapped ) {
            iam_data.st = 'mobzeit';
        } else {
            iam_data.st = 'zeitonl';
        }

        window.iom.c( iam_data, 1 );

        if ( debugMode ) {
            console.log( '[zonTriggeredEventTracking] IVW data sent: ' );
            console.log( iam_data );
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
        }

    };

    /* -------------------------------------------------------------------------
    Dispatch functions: filter the incoming messages and match them to specific
    handlers.
    ------------------------------------------------------------------------- */

    _functions.dispatch.dispatchTrackingMessages = function( messageDataObject ) {

        if ( messageDataObject.sender === 'videojs' ) {
            _functions.handleSpecificPlugin.trackVideojsEvent( messageDataObject.event );
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
            typeof messageDataObject.sender !== 'string'  ||
            typeof messageDataObject.event !== 'string' )
            {
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
    Register the event handler for postes messages
    ------------------------------------------------------------------------- */
    init = function() {

        debugMode = document.location.search.indexOf( 'triggered-event-tracking-debug' ) > -1;

        $( window ).on( 'message', function( event ) {
            _functions.dispatch.dispatchAllMessages( event );
        } );

    };

    return {
        init: init
    };
});
